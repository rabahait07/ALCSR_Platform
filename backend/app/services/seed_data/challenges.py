"""Coding challenges. Each is run and tested in the browser by Pyodide, never on the server."""

from app.models.enums import Difficulty
from app.services.seed_data.types import SeedChallenge

_FIZZBUZZ_DESCRIPTION = """\
## FizzBuzz Sequence

Write a function `fizzbuzz(n: int) -> list[str]` that returns a list of strings for the
numbers from `1` to `n` **inclusive**, in order.

For each number `i`:

- if `i` is a multiple of both 3 and 5, the string is `"FizzBuzz"`
- otherwise, if `i` is a multiple of 3, the string is `"Fizz"`
- otherwise, if `i` is a multiple of 5, the string is `"Buzz"`
- otherwise, the string is the number itself, converted with `str(i)`

### Examples

| Call | Returns |
| --- | --- |
| `fizzbuzz(3)` | `["1", "2", "Fizz"]` |
| `fizzbuzz(5)` | `["1", "2", "Fizz", "4", "Buzz"]` |

### Constraints

- `1 <= n <= 1000`
- Return the list. Do not print it.
- Every item in the list must be a string.

### Hint

Use the modulus operator `%` to test for a multiple, and check for a multiple of both
3 and 5 **before** checking for either one alone.
"""

_FIZZBUZZ_STARTER = """\
def fizzbuzz(n: int) -> list[str]:
    # Write your solution here
    pass
"""

_BINARY_SEARCH_DESCRIPTION = """\
## Binary Search

Binary search is one of the standard searching algorithms in OCR H446 Paper 2
(2.3.1 Algorithms). It finds an item in a **sorted** list by repeatedly halving the
part of the list that could still contain it.

Write a function `binary_search(arr: list[int], target: int) -> int` where `arr` is a
list of integers sorted in **ascending** order.

- If `target` is in `arr`, return its **0-based index**.
- If `target` is not in `arr`, return `-1`.

### Algorithm

1. Keep two pointers, `low` and `high`, at the first and last index still being searched.
2. While `low <= high`, find the midpoint `mid = (low + high) // 2`.
3. If `arr[mid]` is the target, return `mid`.
4. If `arr[mid]` is less than the target, search the upper half: `low = mid + 1`.
5. Otherwise search the lower half: `high = mid - 1`.
6. If the pointers cross, the target is not in the list: return `-1`.

### Example

| Call | Returns |
| --- | --- |
| `binary_search([2, 5, 8, 12, 16, 23, 38], 23)` | `5` |
| `binary_search([2, 5, 8, 12, 16, 23, 38], 10)` | `-1` |

### Time complexity

Your solution should run in `O(log n)` time: each comparison must halve the number of
items left to search. Checking every item in turn is a linear search, `O(n)`, and is
not a binary search.

### Edge cases

- An empty list: return `-1`.
- A list with a single element.
- A target that is not in the list, including one smaller or larger than every item.

### Constraints

- `arr` is sorted in ascending order and contains no duplicates.
- Do not use `in`, `list.index()` or any library search function.
"""

_BINARY_SEARCH_STARTER = """\
def binary_search(arr: list[int], target: int) -> int:
    # Implement binary search on a sorted list
    # Return the index of target, or -1 if not found
    pass
"""

_SORTED_NUMBERS = [2, 5, 8, 12, 16, 23, 38]

CHALLENGES: tuple[SeedChallenge, ...] = (
    SeedChallenge(
        slug="fizzbuzz",
        spec_code="2.2.1",
        title="FizzBuzz Sequence",
        difficulty=Difficulty.EASY,
        function_name="fizzbuzz",
        description=_FIZZBUZZ_DESCRIPTION,
        starter_code=_FIZZBUZZ_STARTER,
        test_cases=(
            {
                "input_args": [3],
                "expected": ["1", "2", "Fizz"],
                "description": "n = 3 (single Fizz)",
            },
            {
                "input_args": [5],
                "expected": ["1", "2", "Fizz", "4", "Buzz"],
                "description": "n = 5 (Fizz and Buzz)",
            },
            {
                "input_args": [15],
                "expected": [
                    "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
                    "11", "Fizz", "13", "14", "FizzBuzz",
                ],
                "description": "n = 15 (includes FizzBuzz)",
            },
            {
                "input_args": [1],
                "expected": ["1"],
                "description": "n = 1 (edge case)",
            },
        ),
    ),
    SeedChallenge(
        slug="binary-search",
        spec_code="2.3.1",
        title="Binary Search",
        difficulty=Difficulty.MEDIUM,
        function_name="binary_search",
        description=_BINARY_SEARCH_DESCRIPTION,
        starter_code=_BINARY_SEARCH_STARTER,
        test_cases=(
            {
                "input_args": [_SORTED_NUMBERS, 23],
                "expected": 5,
                "description": "Target present in upper half",
            },
            {
                "input_args": [_SORTED_NUMBERS, 2],
                "expected": 0,
                "description": "Target at first index",
            },
            {
                "input_args": [_SORTED_NUMBERS, 38],
                "expected": 6,
                "description": "Target at last index",
            },
            {
                "input_args": [_SORTED_NUMBERS, 10],
                "expected": -1,
                "description": "Target not in list",
            },
            {
                "input_args": [[], 5],
                "expected": -1,
                "description": "Empty list edge case",
            },
        ),
    ),
)
