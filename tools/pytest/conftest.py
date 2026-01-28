import os
import sys
import tempfile

import pytest

# conftest.py მდებარეობს: tools/pytest/conftest.py
# პროექტის root არის ერთი დონით ზემოთ: /home/sysop/Code/EarthQuakeWatch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src import create_app
from src.config import TestConfig
from src.commands import init_db_core, populate_db_core


@pytest.fixture
def app():
    """Flask აპი ტესტისთვის: ცალკე SQLite ფაილური ბაზით და სუფთა schema-ით."""
    # დროებითი DB ფაილი
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(TestConfig)
    app.config.update({"SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_path + ".db"})

    with app.app_context():
        # ვქმნით ყველა ტაბლებს საერთო core ლოგიკით (Click CLI-ს გარეშე)
        init_db_core()
        # ვავსებთ DB-ს საწყისი მონაცემებით (თუ საჭიროა)
        populate_db_core()

    try:
        yield app  # ტესტები აქ შესრულდება
    finally:
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI runner (თუ CLI command-ებს ტესტავ)."""
    return app.test_cli_runner()