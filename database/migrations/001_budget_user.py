from playhouse.migrate import *

database = SqliteDatabase("local.db")
migrator = SqliteMigrator(database)

budget = FloatField(default=0)

if database.table_exists("user") and budget not in database.get_columns("user"):
    migrate(migrator.add_column("user", "budget", budget))
