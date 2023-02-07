import interpreter

while True:
    text = input()
    if text == "exit":
        break
    result, error = interpreter.main(text)

    for i in error:
        if i: print(i.error_string())
    else:
        print(result)

