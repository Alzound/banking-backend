from decimal import Decimal, ROUND_HALF_UP


def withdraw_with_fee(accounts, account_id, amount):

    # Verificar que la cuenta exista
    if account_id not in accounts:
        return {
            "success": False,
            "balance": None
        }

    # Verificar que el monto sea válido
    if amount <= 0:
        return {
            "success": False,
            "balance": accounts[account_id]
        }

    # Calcular la comisión del 2 %
    fee_rate = Decimal("0.02")
    fee = amount * fee_rate

    # Redondear la comisión a dos decimales
    fee = fee.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    # Costo total del retiro
    total_cost = amount + fee

    # Verificar saldo suficiente
    if accounts[account_id] >= total_cost:
        accounts[account_id] -= total_cost

        return {
            "success": True,
            "balance": accounts[account_id]
        }

    # Saldo insuficiente
    return {
        "success": False,
        "balance": accounts[account_id]
    }