import importlib
import os
import sys


def load_database_module():
    if 'backend.app.database' in sys.modules:
        del sys.modules['backend.app.database']
    return importlib.import_module('backend.app.database')


def test_uses_env_database_url():
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    db = load_database_module()
    assert db.DATABASE_URL == 'sqlite:///:memory:'
    assert str(db.engine.url) == 'sqlite:///:memory:'
    db.engine.dispose()


def test_default_database_url():
    os.environ.pop('DATABASE_URL', None)
    db = load_database_module()
    assert db.DATABASE_URL == 'postgresql://postgres:%40bcd1234.%2A@localhost:5432/testdb'
    assert db.engine.url.host == 'localhost'
    assert db.engine.url.username == 'postgres'
    db.engine.dispose()
