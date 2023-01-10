# Schnapsen

## Getting started

To get to know the concept of the game, please visit
[this web page](https://www.pagat.com/marriage/schnaps.html).

This is the improved platform for the schnapsen card game.

Python3.9 is highly recommended. To get started, install the schnapsen package in editable mode by running:

```sh
pip install -e .
```

To run the tests, run:

```sh
pip install -e '.[test]'
pytest ./tests
```

If above doesn't work, try deactivating your python and activating again (or just turn off and back on your console).

To test run the GUI, run:

```sh
python executables/server.py
```

You will find bot examples in the [`src/schnapsen/bots`](./src/schnapsen/bots) folder and executable examples in the executables folder.

## Troubleshooting

### [Getting started](#getting-started) doesn't work.

Most of the time, when you read Github python repo READMEs, they won't tell you how to do things in detail, but simply tell you things like run `python bar`, run `pip install foo`, etc. All of these imply that you are running things in an isolated python environment. Often times this is easily done by creating virtual environments (e.g., venv, conda, etc.), where you know exactly what `python`, `pip`, and other modules you are running. If you are not familiar with it and still want to proceed on your current machine, especially on Windows, below are some tips.

1. **Be super specific with your python binary.**

   Don't just run `python bar` but do more like `python3.9 bar`. If you just run `python bar`, it's hard to know which python binary file your system is running.

2. **Be super specific with the modules (e.g., pip, pytest).**

   Don't just run `pip install foo` but do more like `python3.9 -m pip install foo`. Again, if you just run `pip install foo`, we don't know exactly which `pip` your system will run. `python3.9 -m pip install foo` specifies that you want your `python3.9` to run the module (i.e., `-m`) `pip` to do something. The same goes for `python3.9 -m pytest ./tests`, instead of `pytest ./tests`.

Things can be messy if you have multiple python3.9 versions (e.g., `python3.9.1`, `python3.9.10`, etc.). Things can get even more messy when your python binary can't be run as `python3.9` but more like `py3.9` or something. Good luck!
