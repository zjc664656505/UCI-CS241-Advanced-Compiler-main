# UCI-CS241-Advanced-Compiler-main 2023 Winter
1. This project is a humble implementation of DLX SSA-based compiler for the course CS241 Advanced Compiler Class taught by Professor Michael Franz in 2023 winter at UC Irvine by Junchen Zhao. 
2. For running the compiler project, python version needs to be > python3.7+.
3. This project is splitted into 2 parts:
   1. The warmup project: A simple interpreter running the parser in the backend to do the parsing tests on dlx basic algebra computation. The warmup project can be simply run by entering the warmup project folder and do > python run_interpreter.py.
   2. The main SSA-based compiler: For running the code and test the results, please do > python main.py. For testing the compiler with different test code written in dlx, we can add new files in txt file and save it to the test directory. Then change the file name in main.py.
4. Since this project is written individually, coloring and functions for the compiler are not implemented. This compiler includes basic algebra operation compilation, if statement, while statement, and array data structure handlement.

