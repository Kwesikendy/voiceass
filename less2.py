with open("try.docx", "w") as f:
    f.write("Some random text just to explain to the latecomer how to write")

with open("try.txt", "a") as f:
    f.write("Now she has gotten how to write despite the fact that she was late")

with open("try.txt", "r") as f:
    c = f.read()
    print(c)