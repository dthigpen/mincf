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