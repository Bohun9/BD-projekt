import psycopg2
from psycopg2 import sql, extras
from flask import g, current_app
import sys
import click
from werkzeug.exceptions import abort


def get_cursor():
    if "connection" not in g:
        print(f"connecting to db: {current_app.config['DATABASE']}")
        try:
            g.connection = psycopg2.connect(dbname=current_app.config["DATABASE"])
            g.cursor = g.connection.cursor(cursor_factory=extras.DictCursor)
        except psycopg2.OperationalError as e:
            print(e)
            sys.exit(1)
    return g.cursor


def close_db(e=None):
    connection = g.pop("connection", None)
    cursor = g.pop("cursor", None)
    if connection is not None:
        print(f"closing connection db: {current_app.config['DATABASE']}")
        assert cursor is not None
        connection.commit()
        cursor.close()
        connection.close()


def init_db():
    with current_app.open_resource("schema.sql", mode="rb") as f:
        get_cursor().execute(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def add_row_to_table(name, content):
    field_names = tuple(content.keys())
    field_values = tuple(content.values())
    try:
        get_cursor().execute(
            sql.SQL("INSERT INTO {}({}) VALUES %s").format(
                sql.Identifier(name),
                sql.SQL(", ").join(map(sql.Identifier, field_names)),
            ),
            (field_values,),
        )
    except psycopg2.OperationalError as e:
        print(e)
        abort(500, str(e))


def get_table(name):
    cur = get_cursor()
    cur.execute(sql.SQL("SELECT * FROM {};").format(sql.Identifier(name)))
    return cur.fetchall()
