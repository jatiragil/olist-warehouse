from src.utils.validation import validate_rows
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Test 1: rows valid
print("\n=== Test 1: rows valid ===")
rows_valid = [
    ("order1", 1, 20240101),
    ("order2", 2, 20240102),
    ("order3", 3, 20240103),
]
validate_rows(rows_valid, "test_table")


# Test 2: rows kosong
print("\n=== Test 2: rows kosong ===")
try:
    validate_rows([], "test_table")
except ValueError as e:
    logger.error(f"Caught: {e}")


# Test 3: ada NULL
print("\n=== Test 3: ada NULL ===")
rows_null = [
    ("order1", 1, 20240101),
    ("order2", None, 20240102),    # customer_key NULL
    ("order3", 3, 20240103),
]
validate_rows(rows_null, "test_table")


# Test 4: ada duplikat
print("\n=== Test 4: ada duplikat ===")
rows_dup = [
    ("order1", 1, 20240101),
    ("order1", 1, 20240101),       # duplikat
    ("order3", 3, 20240103),
]
validate_rows(rows_dup, "test_table")