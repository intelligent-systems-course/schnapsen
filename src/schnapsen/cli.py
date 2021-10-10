import importlib
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


@main.command()
@click.option("--module-name", default=".")
def load_schnapsen_bot(module_name: str):
    # importing the module also registers it with the BOT_REGISTRY
    importlib.import_module(module_name)
