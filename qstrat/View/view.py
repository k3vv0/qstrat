from pandas import Timestamp

from qstrat.Data.stock import Quote, Transaction, Position


def view(obj: any):
    if isinstance(obj, Quote):
        view_quote(obj)
    elif isinstance(obj, Transaction):
        view_transaction(obj)
    elif isinstance(obj, Position):
        view_position(obj)
    else:
        print("Object not recognized.")


def view_quote(quote: Quote):
    """
    View the quote.
    :param quote:
    :return:
    """

    vd = quote.view_data()
    print()
    print("=====================================")
    print(f"{vd['ticker']} Quote")
    print(f"\tPrice: {vd['curr_price']}")
    print(f"\tDate: {vd['date']}")
    print(f"\tTime: {vd['time']}")
    print("=====================================")


def view_transaction(transaction: Transaction):
    """
    View the transaction.
    :param transaction:
    :return:
    """

    vd = transaction.view_data()
    print()
    print("=====================================")
    print(f"{vd['ticker']} ({vd['type']}) Transaction")
    print(f"\tPrice: {vd['executed_price']}")
    print(f"\tQuantity: {vd['quantity']}")
    if vd['quantity'] > 0:
        print(f"\tValue: ${vd['value']:,.2f}")
    elif vd['quantity'] < 0:
        print(f"\tValue: -${abs(vd['value']):,.2f}")
    print(f"\tDate Time: {vd['date_time']}")
    print("=====================================")


def view_position(cons: Position):
    """
    View the consolidated security.
    :param cons:
    :return:
    """

    vd = cons.view_data()
    print()
    print("=====================================")
    print(f"{vd['ticker']} Position")
    print(f"\tPurchase Value: {vd['purchase_value']}")
    print(f"\tCurrent Value: {vd['current_value']}")
    print(f"\tQuantity: {vd['quantity']}")
    print(f"\tStart Date: {vd['start_date']}")
    print(f"\tEnd Date: {vd['end_date']}")
    print("=====================================")


if __name__ == "__main__":
    q = Quote("NVDA")
    view(q)
    buy = Transaction("NVDA", 100, timestamp=Timestamp("2021-01-13"))
    view(buy)
    sell = Transaction("NVDA", -50, timestamp=Timestamp("2023-01-13"))
    view(sell)
    pos = Position("NVDA", initial_transaction=buy)
    pos2 = Position("NVDA", initial_transaction=buy)
    view(pos)
    pos.stack_transaction(sell)
    view(pos)
    pos.stack_transaction(Transaction("NVDA", -25, timestamp=Timestamp("2024-04-15")))
    view(pos)
