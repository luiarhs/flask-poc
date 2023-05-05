import sqlite3
import click
from flask import current_app, g

def get_db(prod = False):
    """
    Return a connection to a sqlite database. Set prod = True for the production
    database, or prod = False (the default) for the test database.
    """
    if prod:
        db_name = current_app.config["PROD_DATABASE"]
    else:
        db_name = current_app.config["TEST_DATABASE"]
    if "db" not in g:
        g.db = sqlite3.connect(
            db_name,
            detect_types = sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e = None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(prod = False):
    """
    Initialise the production or test database. Set prod = True for the 
    production database, or prod = False (the default) for the test database.
    """
    db = get_db(prod = prod)
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

@click.command("init-test-db")
def init_test_db_command():
    """
    Drop existing and create new tables in the test database.
    """
    init_db()
    click.echo("Initialized the test database.")

@click.command("init-prod-db")
def init_prod_db_command():
    """
    Drop existing and create new tables in the production database.
    """
    init_db(prod = True)
    click.echo("Initialized the production database.")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_test_db_command)
    app.cli.add_command(init_prod_db_command)
