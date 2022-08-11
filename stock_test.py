
from app.stock_comparison import get_custom_data, stock_information
import pytest

def test_stock_symbol():

    # with invalidate input date, an error shows up and the app stops running
    ERROR_MSG = "TEST1 is not a valid stock symbol. Please re-enter."

    with pytest.raises(SystemExit, match=ERROR_MSG):
        stock_information(symbol="test1")



def test_custom_data(capsys):

    # with invalidate input date, an error shows up and the app stops running
    
    error_message_1 = "Your input is invalid. Please enter a date that both stocks are listed."
    error_message_2 = "Your input is invalid. Please enter a historical date."
    error_message_3 = "Your input date format is incorrect. Please use YYYY-MM-DD."

    with pytest.raises(SystemExit, match=error_message_1):
        get_custom_data(input_date="2001-10-30", symbol_1="googl", symbol_2="amzn")
    with pytest.raises(SystemExit, match=error_message_2):
        get_custom_data(input_date="2022-10-30", symbol_1="googl", symbol_2="amzn")
    with pytest.raises(SystemExit, match=error_message_3):
        get_custom_data(input_date="123/45", symbol_1="googl", symbol_2="amzn")
    


