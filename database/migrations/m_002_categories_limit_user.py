from playhouse.migrate import *
from playhouse.sqlite_ext import JSONField


def categories_limit_002():
    database = SqliteDatabase("local.db")
    migrator = SqliteMigrator(database)

    categories_limit = JSONField(default={})

    if database.table_exists("user") and categories_limit not in database.get_columns("user"):
        migrate(migrator.add_column("user", "categories_limit", categories_limit))
