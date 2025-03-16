import os

import pytest

os.environ["PYTEST_RUNNING"] = "True"

from database.entities import User

User.create_table()


def test_should_insert_user():
    test_email = "test@user.com"
    User.insert_user(test_email, "password123")

    assert User.get_user_where_email(test_email).email == test_email


def test_should_insert_multiple_users():
    test_email = "test_2@user.com"
    test_email2 = "test_3@user.com"

    User.insert_user(test_email, "password123")
    User.insert_user(test_email2, "password123")

    assert User.get_user_where_email(test_email).email == test_email
    assert User.get_user_where_email(test_email2).email == test_email2

def test_should_not_insert_user_with_same_email():
    test_email = "test@user.com"

    with pytest.raises(Exception) as exc_info:
        User.insert_user(test_email, "password123")
    
    assert "UNIQUE constraint failed: user.email" in str(exc_info.value)

def test_should_get_all_users():
    users = User.get_all_users()

    # three users were inserted during previous tests
    assert len(users) == 3

def test_should_get_user_where_email():
    test_email = "test@user.com"

    user = User.get_user_where_email(test_email)

    assert test_email == user.email

def test_should_not_get_user_when_not_found():
    test_email = "not_found@user.com"

    with pytest.raises(Exception) as exc_info:
        User.get_user_where_email(test_email)

    assert "instance matching query does not exist" in str(exc_info.value)

def test_should_set_users_budget():
    test_email = "test@user.com"
    user = User.get_user_where_email(test_email)

    assert user.budget == 0.0

    User.set_user_budget(user_id=user.id, budget=21.37)

    assert User.get_user_where_email(test_email).budget == 21.37