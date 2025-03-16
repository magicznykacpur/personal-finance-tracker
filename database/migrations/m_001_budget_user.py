from playhouse.migrate import *


def budget_user_001():
    database = SqliteDatabase("local.db")
    migrator = SqliteMigrator(database)

    budget = FloatField(default=0)

    if database.table_exists("user") and budget not in database.get_columns("user"):
        migrate(migrator.add_column("user", "budget", budget))
