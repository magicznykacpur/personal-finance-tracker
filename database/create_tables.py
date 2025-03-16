from entities import Transaction, User
from peewee import SqliteDatabase

sqlite_database = SqliteDatabase("local.db")


User.create_table()
Transaction.create_table()