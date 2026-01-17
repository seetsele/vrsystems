import pytest
from pathlib import Path


@pytest.mark.unit
def test_migration_sql_exists():
    root = Path(__file__).resolve().parents[2]
    migrations = root / 'database' / 'migrations'
    assert migrations.exists(), 'migrations directory missing'
    sqls = list(migrations.rglob('*.sql'))
    assert len(sqls) > 0, 'no migration SQL files found'
