import importlib
import click


@click.group()
def main() -> None:
    """The main entry point."""


# @main.group()
# def fuzzers():
#     "Commands for fuzzing stuff"


@main.command()
@click.option("--module-name", default=".")
def load_schnapsen_bot(module_name: str) -> None:
    import sys
    # Adding the empty directory -- seems to be the cwd to the path.
    # This makes it possible to load bots which are in suer defined modules
    sys.path.insert(0, "")
    # importing the module also registers it with the BOT_REGISTRY
    importlib.import_module(name=module_name)
    # taking the entry back out of the path. Not sure what that will do...
    sys.path.pop(0)
