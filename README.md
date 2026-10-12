# Nook
A scope-centric scripting language

## pynook vs Nook
Pynook is the first implementation of the nook programming language, and is still experimental. It is written entirely in python and consists of an custom intermediate representation language that is consumed by a custom built virtual machine. 

## Philosophy
Nook is scope-centric programming language for distributed systems designed to be simple, easy to learn, and ergonomic. Scopes are first-class citizens in Nook, serving as the foundation for objects, functions, modules, and execution contexts. The language minimizes reserved words, favoring syntax and scope relationships over specialized language constructs. Nook provides powerful reflection and serialization capabilities. JSON is a subset of Nook, enabling seamless interoperability between static configuration and executable code. 

Nook's long-term vision is to provide a foundation for distributed infrastructure, rapid iteration, executable knowledge sharing and semantic code search. By treating scopes as portable, addressable, and serializable runtime artifacts, Nook aims to make distributed software systems easier to build, discover, and evolve.

## Setup with pynook
Clone the repo, and then create a shim for running the interpreter:

    git clone ...
    New-Item -ItemType File nook.ps1 # place in PATH

Once that is done, edit shim (nook.ps1):

    py "<path/to/nook/repo>/nook.py" @args

The pynook interpreter does not require any external python dependencies.

## Your First Nook Program: Hello World

Navigate to a folder where you'd like to store you .nk files, and create a new file with whatever name you'd like, such as `hello.nk`. Add the following to it:

    print('hello world from nook!')

Run the interpreter via your shim, so like:

    nook hello.nk

The pynook interpreter should print `"hello world"` on screen.

## Overview of Nook

### Scopes are Objects, Objects are Scopes
Nook is a *scope based* language. Scopes are objects, and objects are scopes. When you ran `hello.nk`, a 'main' scope was created, and then a *file* scope was created with the main scope as its parent. The file scope is where you wrote `print(...)`. These respective scopes can be accessed through the __file__ and __main__ keywords.

Scopes can also be created with JSON syntax. JSON is actually a subset of the Nook language:

    my_scope: {
        my_obj: "hi!",
        my_other_obj: 55
    }

One quirk of Nook is that `=` is not used for assignment. Instead, `:` is used. `=` is still used in boolean operators such as `==`, `<=`, and `>=`.

You might have noticed that I introduced some primitive types in the example above. Nook has primitives for `string`, `int`, `float`, `boolean`, `binary`, `hexadecimal`, `list`, and `set`. Types are dynamically attached during assignment.

### Name Resolution.
Every scope has a parent scope. When a variable name is referenced, resolution climbs from the current scope and up it's parent tree until it finds a matching name. Member access does not climb the parent tree and throws an error if the member does not exist. (i.e. `a.b` does not climb the scope tree to look for b, allowing the statement to throw and error when `b` does not exist as a member of `a`).

Builtins live in the implicit 'builtins' scope that the runtime creates at the root of the scope tree, and the entry file constitutes the first user defined scope in the tree (a direct child of the builtins scope). This user defined scope also defined the "__main__" member, which points to itself.

    a: 5
    b: {
        c: {
            d: a # works! 'a' is found through climbing the scope tree
        }
    }

    # throws an exception:
    b.a  
    # 'a' is not a member of b. Member access does not climb the scope tree.

    __main__ == __file__ # true, assuming this code exists in the entry file for the program


## Language Constructs

In the runtime, every scope contains members, a name (which can be `none`), and a parent (only the `builtins` scope has a parent of value `none`). Keep this in mind as you read about the language.

### Primitives

    my_int: 5
    my_string: "good day to you human!"
    my_float: 55.32
    my_int: 56
    my_boolean: false # or true
    my_binary: b1001110
    my_hexadecimal: 5566ffdde
    my_list: [1, 2, "hello", true]
    my_set: set[1, 2, "hello", "hello"] # will only contain one "hello" after assignment

### Scope-Objects

    my_scope: {
        obj: "hi",
        field: 'hello',
        number: 101,
        my_list: [3, 5, 77, 4]
    }

### Destructuring

    { obj, field }: my_scope # obj and field become available in the current scope

### Subscript
    
    # subscripts on scope objects are interchangeable with dot notation (javascript-style)
    my_scope["field"] == my_scope.field 

    # subscripts on lists and sets take integers, and return the item at the matching index:
    my_list[0] == 3

### if..else

    if my_scope.obj == "hi" {
        print('hello!')
    }

    elif my_scope.obj == "huh" {
        print('ah, I see you are confused')
    }

    else {
        print('goodbye, I loved you.')
    }

### for

    for i: 0; i < 20; i: i+1 {
        print(i)
    }

    # prints 0 through 19

### for..in

    some_list: [1, 2, 3, 4, 5]

    acc: 0
    for item in some_list {
        acc: acc + item
        print(acc)
    }

    # prints fibbonacci sequence

### while

    a: 1
    while a <= 99 {
        print(a)
        a: a+2
    }

    # prints odd numbers, 1 through 99

### do...while

    acc: 0
    do {
        acc: acc + 1
        print(acc)
    } while acc < 200

    # prints 0 through 200


### Deferred Scopes (Functions)

A deferred scope is a scope whose body has not been executed. When deferred scopes are executed, they create a copy of themselves for the execution, leaving the original state of the deferred scope untouched.  

    my_function: (param1, param2) {
        print(param1, param2)
    }

    # instance becomes a copy of my_function, but with the 
    # parameter definition and body definition of my_function having been ran.
    instance: my_function('hello', 'world')

### Root Functions

Sometimes it is handy to have an easy reference to an important ancestor to a scope. The `root` keyword is great for this. Any function that has `root` as its first parameter will assign `root` to that function's __scope__ reference:

    my_root_function: (root, unimportant_param) {
        __scope__ == root # true
        a: 55 
        method: () {
            __scope__ == root # false
            a: 77
            print(root.a) # prints 55
        }
    } 

`root` can be shadowed by other `root` declarations, similar to any other variable.

### Default Parameter Values
Default parameter values can be written the same as assignments in Nook:

    func: (a, b: "default_value") {
        print(a)
        print(b)
    }

    func(1) # prints "1 default_value"

### try..catch

Exceptions can be thrown via the `throw` keyword, to be caught in a parent scope:
    
    some_func: () {
        throw Exception('throw me!')
    }

    try {
        some_func()
    } catch e {
        print(e.message)
    } finally {
        print('all done!')
    }

Exceptions are just scope objects. There are no special rules for them.

### Spread Operator

    my_scope_copy: { ..my_scope, new_entry: "extra" }
    my_list_copy: [ ..my_scope.my_list, "new item!" }

    # can also be used on function parameters as a postfix for capturing remaining arguments:

    my_func: (arg1, rest..) {
        type(rest) == types.LIST
    }

    # as well as used in arguments to distribute items per parameter:

    my_func(my_scope..) # scopes will match field names to parameter names
    my_func(my_list..) # lists will just distribute based on the order of the items

### Collect, Leave, Return (Control Flow and Scope Promotion)

There is no `break` keyword in Nook, like other c-like languages. Instead, Nook leans into it's scopey-ness, and introduces to new keywords: `leave` and `collect`. `return` behaves the same as other c-like languages, returning some value to the nearest return scope outside the current function definition.

`leave` is similar to `break`, but it can be used outside of loops. `leave` always stops the execution of the current scope, whether that scope belongs to a `while` loop, `switch case`, or function body.

`collect` is the most interesting of the three. `collect` exits to the nearest scope definition or switch scope and also *promotes variables from the current scope to the scope it exits to*. Look at the switch..case section for an example of how it can be used to enable fallthrough behavior.

### switch..case
    
    a: "prev"

    switch a {
        case "prev" {
            print("previous!")
            a: "next"
            collect a
        }

        case "next" {
            # collect keyword promotes `a` from the previous scope, so the following block runs:
            print("next!")
        }
    }

As this example indicates, Nook reevaluates the switch expression per case, allowing cases to cascade on eachother via state mutation.

## Builtins
Nook has builtin scopes for file/stream io, AST and JSON serialization, math, and module imports. 

### `import` builtin
`import` is a builtin scope function that can be used in several ways. It plays well with destructuring as well as the spread operator. 

    # imports all names in module_name's __file__ scope into the current scope.
    ..import('module_name') 

    # stores module_a's __file__ scope in the variable `module_a`
    module_a: import('module_a') 

    # adds matching named func1, func2 from module_a to variables func1, func2 in current scope
    { func1, func2 }: import('module_a') 

    # import can also be used on json files, since json is just a subset of nook:
    { json_data }: import ('myjsonfile.json')

### Other builtins
`stdout`, `stdin`, `stderr`, `open`, `close`, `write`, `execute`, `seek`, `print`

### `print` builtin
Nook's print function is smarter than many other c-like language `print`s. `print` can be used to 
pretty print scopes, lists, and sets, as well as simply print text to screen. When you want to 
use something more lightweight, use `stdout` instead.

    print(json(some_scope)) # pretty prints with default indentation and depth levels
    print(some_scope) # works exactly the same, as print knows how to convert scopes to json strings.
    print(some_scope, indent: 2, depth: 20) # pretty prints with specified indent and depth values.

## Standard Library
Nook's standard library (seperate from the builtins) is entirely written in Nook.

## Future Development

Nook is still in an experimental phase, but some language-feature plans for the future include:

    - File/Stream IO builtins
    - json builtins
    - async..await
    - `net` primitives focused on peer to peer networking
    - Scope AST Hashes as Addresses for remote functions
    - AST serialization (utilizing Scope Addresses)
    - Static Scope Members via UncalledObj.member or __scope__.shared or root.shared
    - Decentralized AST lookup and sharing/searching via hypervectors in addition to traditional documentation

The long term runtime plan is to bootstrap Nook's compilation to the Nook IR, and then rewrite the virtual machine in c.
