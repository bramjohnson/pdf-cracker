with open('words.txt', encoding='utf8') as file:
    words = [line.rstrip() for line in file]
    words = [x for x in words if x[0].islower()]
    words = [x for x in words if '-' not in x]
    words = [x for x in words if len(x) < 10]
    words = [x + "\n" for x in words]
    with open('small-words.txt', 'w', encoding='utf8') as new_file:
        new_file.writelines(words)