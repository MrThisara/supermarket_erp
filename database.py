import sqlite3
import click
import flask
from flask import g, current_app

def get_db(app=None):
    if app:
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        return conn
    
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = get_db(app)
        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
            db.commit()

@click.command('init-db')
def init_db_command():
    from app import create_app
    app = create_app()
    init_db(app)
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)