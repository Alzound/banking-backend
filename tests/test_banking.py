import pytest
from decimal import Decimal
from app.banking import withdraw_with_fee

@pytest.mark.parametrize(
    "balance, amount, expected_success, expected_balance", 
    [
        (Decimal("1000.00"), Decimal("100.00"), True, Decimal("898.00")),
        (Decimal("100.00"), Decimal("100.00"), False, Decimal("100.00")),
        (Decimal("102.00"), Decimal("100.00"), True, Decimal("0.00")),
        (Decimal("50.00"), Decimal("-10.00"), False, Decimal("50.00")),
        (Decimal("100.00"), Decimal("0.01"), True, Decimal("99.99")),
    ]
)

def test_withdraw_fee_cases(balance, amount, expected_success, expected_balance): 
    accounts = {101: balance}

    result = withdraw_with_fee(accounts, 101, amount)

    assert result["success"] is expected_success
    assert result["balance"] == expected_balance
    assert accounts[101] == expected_balance
    