import pytest
from kaliya import check_value

def test_check_value():
    assert check_value("test", "This is ok") == "test"

def test_check_value_fail():
    with pytest.raises(ValueError):
        check_value(None, "Failed check")
