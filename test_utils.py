import pytest
import datetime
import utils

testdata = [
    (datetime.date(2025,10,24), datetime.date(2025,10,24)),
    (datetime.date(2025,10,25), datetime.date(2025,10,24)),
    (datetime.date(2025,10,26), datetime.date(2025,10,24)),
    (datetime.date(2025,10,27), datetime.date(2025,10,24)),
    (datetime.date(2025,10,28), datetime.date(2025,10,24)),
    (datetime.date(2025,10,29), datetime.date(2025,10,24)),
    (datetime.date(2025,10,30), datetime.date(2025,10,24)),
    (datetime.date(2025,10,31), datetime.date(2025,10,31)),
]

@pytest.mark.parametrize("input, expected", testdata)
def test_get_current_or_last_session_start_date(input: datetime.date, expected: datetime.date) -> None:  
    result = utils.get_current_or_last_session_start_date(input) 
    assert result == expected