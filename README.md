# mincf
Write .mcfunction files with a shorter, more concise syntax.

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

## Installation

## Usage
Start the process with
```
> python mincf.py output_pack_path
```
For more information use the `--help` option
```
> python mincf.py --help
usage: mincf.py [-h] [-s SRC] dest

Write more concise mcfunction syntax

positional arguments:
  dest               Destination datapack directory to output to

optional arguments:
  -h, --help         show this help message and exit
  -s SRC, --src SRC  Source datapack directory to monitor
```

## TODO
 - Update installation and usage sections
 - Handle directory changes
