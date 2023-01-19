import interpreter

while True:
    text = input('Parser: ')
    result, error = interpreter.main(text)

    for i in error:
        if i: print(i.error_string())
    else:
        for i in result:
            print(i)

