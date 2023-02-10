class Constants:
    SCANNER_IDENTIFIER_ADDRESS_OFFSET:int = 0
    FILE_READER_END_OF_FILE_CHAR:int = 255

    ARRAY_ADDRESS_OFFSET:int = 500
    INSTRUCTION_START_COUNTER:int = 0
    BLOCK_START_COUNTER:int = 0
    FORMAL_PARAMETER_VERSION:int = -2 #-1
    GLOBAL_VARIABLE_VERSION:int = -3 #-2
    NUMBER_OF_INSTRUCTIONS_CAP:int = 10000

    CLUSTER_OFFSET:int = 10000
    REGISTER_SIZE:int = 8
    SPILL_REGISTER_OFFSET:int = 100
    BYTE_SIZE:int = 4