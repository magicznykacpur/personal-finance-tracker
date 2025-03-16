# personal-finance-tracker
RESTful API for tracking personal finance

## running project
to run the project:
- `python` version at least `3.12` required
- `optional` create a `venv` using `python3 -m venv` command
- run `install.sh` to `pip install` all the required dependencies
- create a `local.db` sqlite database file, run `create_tables.sh` to populate it
- create a `.env.local` file and set the `JWT_SECRET` variable

after all the steps are completed you can run the server with `main.sh`
`fastapi` will deploy a server on `http://127.0.0.1:8000`
you can view the swagger on `http://127.0.0.1:8000/docs`

## tests
run tests with `test.sh`
