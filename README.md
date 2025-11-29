# Compiler

MiniC is a compiler that translates a small subset of the C programming language to x86 assembly. This is a work in progress. I've written the lexer and parser by hand, using a top-down recursive descent parser to generate the syntax tree. I'll update this readme as I add more functionality to the compiler. The *Test Programs* folder will always contain programs that the compiler succesfully translates, with the most recent commits containing more advanced functionality than those before it. The ultimate goal of this project is to be able to write a compiler powerful enough to handle function calls. Along the way, I'll get to solve many interesting problems such as evaluating expressions and handling iterative constructs!

## Getting Started

Follow these instructions to compile any of the programs in the *Test Programs* folder or any of your own.

### Prerequisites

The compiler runs on **Python 2.7**.

### Installing

Download the repository.

## Running the Test Programs

Say we want to compile and execute the program *more_nested_ops.c* in the *Test Programs* folder. We'll need to run the following commands:

`cd MiniC`

`python main.py Test\ Programs/more_nested_ops.c`

The compiler generates x86 assembly and writes it to a file called *assembly.s*. If you want to view the assembly generated, type:

`cat assembly.s`

Now, we need to run the assembly. To do this, we need to assemble the file we just created.

`gcc -m32 assembly.s -o out`

The `-m32` flag tells gcc to create a 32-bit binary and `out` is the name of the executable we generated.

To run the executable and see what its returns type:

`./out`

`echo $?`

$? is the return code from the last run process. This should output `14` which is the expected output of the program we compiled.

## Error Reporting

I've tried to report errors with as much information as possible. I handle errors while parsing the syntax. I include the line number of the offending statement and in most cases, the missing token (if that's the nature of the error). Of course, you can always try it out by writing a faulty program.

## Inspiration

I have always been curious about compilers; they're immensely complicated tools that we programmers take for granted. Unfortunately, compilers are inaccessible to most undergraduate level students. However with certain resources I was able to start writing a small compiler of my own. Firstly, I owe my thanks to the writers of the Dragon Book for helping me understand how languages are expressed with grammars and the complicated theory of parsing languages. Next, I'd like to thank Abdulaziz Ghuloum for his paper titled *An Incremental Approach to Compiler Construction* which uses small, well-defined steps to incrementally build a compiler. At the end of each step you have a working compiler, with more functionality than the one you had before. Lastly, I'd like to thank Nora Sandler. Her blog posts defined the functionality of the lexer and parser without which I would've found it close to impossible to write the parser by hand.

## Future Plans

I'll work on this project whenever I find time outside of my school work. At some point I'd like to experience working with lexer and parser generator tools such as Lex and Bison. Until then - stay posted!
