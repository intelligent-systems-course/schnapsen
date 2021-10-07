import click
import schnapsen.fizzbuzz


@click.group()
def main():
    """The main entry point."""

@main.group()
def fuzzers():
    "Commands for fuzzing stuff"



@fuzzers.command(name="fizzbuzz", help="Run FizzBuzz")
@click.option("-a", "--start", type=int, default=0, help="The number to start the FizzBuzz from")
@click.option("-e", "--end", type=int, default=100, help="The number to stop the FizzBuzz (inclusive)")
def fizzbuzz(start: int, end: int):
    for i in range(start, end + 1):
        schnapsen.fizzbuzz.fizzbuzz(i)
