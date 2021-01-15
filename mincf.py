import argparse
import os
import re
from threading import main_thread
import shutil
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from enum import Enum
from queue import Queue

DEFAULT_STORAGE = 'call_stack:'

# Assignment

var_path = r'(?:[\w:.]*:)?[\w.]+'
array_literal = r'\[.*\]'
dec_literal = r'\d+(?:\.\d{1,2})?[bfd]?'
string_literal = r'\"(?:[^\\\"]|\\.)*\"'
literals = rf'(?:{dec_literal})|(?:{string_literal})|(?:{array_literal})'
literal_or_var = rf'(?:(?:{literals})|(?:{var_path}))'
assign_regex = rf'({var_path})\s*=\s*({literal_or_var})'

# Function calls
funct_line_with_args_regex = rf'(^.*)(function (?:[\w.]+:)?[\w/]+)\s+({literal_or_var}(?:\s+{literal_or_var})*)$'

CHANGE_DETECTED = False
QUEUE = []

CREATE = 'created'
MODIFY = 'modified'
MOVE = 'moved'
DELETE = 'deleted'

src_dir = None
dest_dir = None

def get_path_from_str(path_str):
    last_colon = path_str.rfind(':')
    
    ns_storage = path_str[:last_colon] if last_colon != -1 else DEFAULT_STORAGE
    path = path_str[last_colon + 1:] if last_colon != -1 else path_str
    return (ns_storage,path)


def format_var_assignment(destination, source):

    dest_var = get_path_from_str(destination)
    is_literal = re.match(literals, source)

    if is_literal:

        return f'data modify storage {dest_var[0]} {dest_var[1]} set value {source}'
    else:
        source_var = get_path_from_str(source)
        return f'data modify storage {dest_var[0]} {dest_var[1]} set from storage {source_var[0]} {source_var[1]}'


def handle_assignments(text):
    return re.sub(assign_regex,lambda m: format_var_assignment(m.group(1),m.group(2)),text)


def format_funct_with_args(pre_funct_call, funct_call, funct_args):
    lines = []
    count = 0
    for arg_match in re.finditer(literal_or_var, funct_args):
        assignment = format_var_assignment(f'call.arg{count}', arg_match.group(0))
        lines.append(pre_funct_call + assignment)
        count += 1
    lines.append(pre_funct_call + funct_call)
    return '\n'.join(lines)


def handle_funct_args(text):
    return re.sub(funct_line_with_args_regex,lambda m: format_funct_with_args(m.group(1),m.group(2),m.group(3)),text,flags=re.MULTILINE)


def convert_to_mcfunction(path):
    with open(path, 'r+') as f:
        text = f.read()
        text = handle_assignments(text)
        text = handle_funct_args(text)
        f.seek(0)
        f.write(text)
        f.truncate()


def on_watchdog_event(event):
    global QUEUE
    if not any(queued_event for queued_event in QUEUE if queued_event.event_type == event.event_type \
        and queued_event.src_path == event.src_path \
        and (event.event_type != MOVE or queued_event.dest_path == event.dest_path)):
        QUEUE.append(event)

def replace_dest_with_src(src, dest):
    shutil.copytree(src, dest,dirs_exist_ok=True)

def is_dest_in_user_dir(dest):
    home = Path.home()
    print(home, dest)
    dest_path = Path(dest)
    return home in dest_path.parents

def convert_all_mcf_files(dest_dir):
    for root, dirs, files in os.walk(dest_dir):
        for filename in [file for file in files if file.endswith('.mcfunction')]:
            convert_to_mcfunction(os.path.join(root, filename))

def handle_fs_change_event(event):
    output_src_path = os.path.join(dest_dir,os.path.relpath(event.src_path, src_dir))
    
    print('EVENT:', event.event_type, event.src_path)
    if event.event_type == CREATE or event.event_type == MODIFY:
        os.makedirs(os.path.dirname(output_src_path), exist_ok=True)
        shutil.copyfile(event.src_path, output_src_path)
    elif event.event_type == MOVE:
        output_dest_path = os.path.join(dest_dir,os.path.relpath(event.dest_path, src_dir))
        # print('Move to', event.dest_path, output_dest_path)
        os.remove(output_src_path)
        os.makedirs(os.path.dirname(output_dest_path), exist_ok=True)
        shutil.copyfile(event.dest_path, output_dest_path)
    elif event.event_type == DELETE:
        os.remove(output_src_path)

    convert_all_mcf_files(dest_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Write more concise mcfunction syntax')
    parser.add_argument('dest',type=str, help='Destination datapack directory to output to')
    parser.add_argument('-s','--src', default=os.getcwd(), type=str, help='Source datapack directory to monitor')
    args = parser.parse_args()
    src_dir = args.src
    dest_dir = args.dest

    if not is_dest_in_user_dir(dest_dir):
        print('! Destination path not in user folder, exiting now !')
        exit(1)

    # Run once initially
    replace_dest_with_src(src_dir, dest_dir)
    convert_all_mcf_files(dest_dir)

    patterns = "*"
    ignore_patterns = ""
    ignore_directories = True
    case_sensitive = True
    pattern_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    
    pattern_event_handler.on_any_event = on_watchdog_event
   
    observer = Observer()
    observer.schedule(pattern_event_handler, src_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
            while len(QUEUE) > 0:
                handle_fs_change_event(QUEUE.pop())
    except KeyboardInterrupt:
        observer.stop()
    observer.join()