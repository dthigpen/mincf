# mincf
Write .mcfunction files with a shorter, more concise syntax. This script will monitor for changes in the datapack directory and convert `mincf` syntax into `mcfunction` syntax in the provided output directory. 

## Examples
```
# Variable assignment
# You can set variables to literals or other variables
this.foo = "bar"
this.array = [{a:1},{foo:"bar"},{}]
this.num = 1
this.float = 3.14
this.float2 = this.float

pack:storage:var = "hello"
this.myvar = pack:storage:var


# Call function with arguments
# Arguments can be literals or variable references
function something:hello/there foo myvar "apple"
this.val = call.result
```
The following command shows it monitoring a datapack development directory and outputs the result to a Mincraft world's datapacks directory.
```
> python mincf.py ~/.minecraft/saves/world1/datapacks/mypack --src ~/dev/mypack
```
Use `Ctrl + C` to quit the program.

## Installation
Install the `watchdog` package so that the program can monitor a directory for changes.
```
> pip install watchdog
```
Clone the repository or download the `mincf.py` script. See the Usage section for how to execute it.

## Usage
Start the process with
```
> python mincf.py output_pack_path --src mincf_pack_path
```
For more information use the `--help` option
```
> py mincf.py --help
usage: mincf.py [-h] [-s SRC] dest

Write more concise mcfunction syntax. Quit the program with "Ctrl + C"

positional arguments:
  dest               destination datapack directory to output to

optional arguments:
  -h, --help         show this help message and exit
  -s SRC, --src SRC  source datapack directory to monitor
```

## TODO
 - Update installation and usage sections
 - Schema support in VS Code with Datapack Helper Plus
 - unit tests
