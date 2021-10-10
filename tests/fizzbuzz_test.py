import pytest

from schnapsen.fizzbuzz import fizzbuzz


@pytest.mark.parametrize(
    'number, word', [
        (1, '1'),
        (3, 'Fizz'),
        (15, 'FizzBuzz'),
        (43, '43'),
        (20, 'Buzz'),
    ]
)
def test_fizzbuzz(capsys, number, word):
    fizzbuzz(number)
    captured = capsys.readouterr()
    assert captured.out == f"{word}\n"
