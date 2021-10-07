

def fizzbuzz(i: int) -> None:
    three_or_five = False
    if i % 3 == 0:
        print("Fizz", end="")
        three_or_five = True
    if i % 5 == 0:
        print("Buzz", end="")
        three_or_five = True
    if not three_or_five:
        print(i, end="")
    print()
