for i in range(1, 101):
    output = "".join(list(map(lambda item: item[1] if not i % item[0] else "", {3: "Fizz", 5: "Buzz"}.items())))
    print([i, output][int(output > str(i))])
