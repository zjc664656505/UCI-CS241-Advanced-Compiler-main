from interpreter import *
'''
const #literal  define a constant 
 
add x y         addition 
sub x y         subtraction 
mul x y         multiplication 
div x y         division 
cmp x y         comparison 
 
adda x y        add two addresses x und y (used only with arrays) 
load y          load from memory address y 
store y x       store y to memory address x 
phi x1 x2       compute Phi(x1, x2) 
end             end of program 
bra y           branch to y 
bne x y         branch to y on x not equal 
beq x y         branch to y on x equal 
ble x y         branch to y on x less or equal 
blt x y         branch to y on x less 
bge x y         branch to y on x greater or equal 
bgt x y         branch to y on x greater 
 
In order to model the built-in input and output routines, we add three more operations: 
 
read            read 
write x         write 
writeNL         writeNewLine 
'''

