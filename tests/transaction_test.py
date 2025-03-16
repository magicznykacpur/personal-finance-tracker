import os

import pytest

os.environ["PYTEST_RUNNING"] = "True"

from database.entities import Transaction, User

User.create_table()
Transaction.create_table()

test_email = "test_transaction@user.com"
User.insert_user(test_email, "password123")

def test_should_create_transaction_for_user():
    user = User.get_user_where_email(test_email)

    Transaction.insert_transaction(
        user=user, amount=69.69, category="Other", description="testing..."
    )

    transactions = Transaction.get_all_transactions_by_user(user)

    assert len(transactions) == 1

def test_should_add_more_transactions_for_user():
    user = User.get_user_where_email(test_email)

    Transaction.insert_transaction(
        user=user, amount=21.37, category="Tech", description="testing 2..."
    )
    Transaction.insert_transaction(
        user=user, amount=420, category="Food", description="testing 3..."
    )
    Transaction.insert_transaction(
        user=user, amount=1337, category="Learning", description="testing 4..."
    )

    transactions = Transaction.get_all_transactions_by_user(user)

    # 3 + 1 from the first test
    assert len(transactions) == 4