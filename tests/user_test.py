from peewee import SqliteDatabase
from database import User


sqlite_database = SqliteDatabase(":memory:")
User.create_table()
user = User()


def test_should_create_user():
    assert user != None


def test_should_insert_user():
    test_email = "test@user.com"
    user.insert_user(test_email, "password123")

    assert user.get_user_where_email(test_email).email == test_email


def test_should_insert_multiple_users():
    test_email = "test_2@user.com"
    test_email2 = "test_3@user.com"

    user.insert_user(test_email, "password123")
    user.insert_user(test_email2, "password123")

    assert user.get_user_where_email(test_email).email == test_email
    assert user.get_user_where_email(test_email2).email == test_email2

def test_should_get_all_users():
    users = user.get_all_users()

    # three users were inserted during previous tests
    assert len(users) == 3