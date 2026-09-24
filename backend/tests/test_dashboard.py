"""Dashboard tests: global vs scoped counts. SQLite only."""
from app.modules.customers.schemas import CustomerCreate
from app.modules.customers.service import create_customer
from app.modules.dashboard.service import get_stats
from app.modules.equipment.models import Equipment


def _seed(db):
    create_customer(db, CustomerCreate(customer_id="C-ES", account_name="ES", country="Spain", subsidiary_id="ES"))
    create_customer(db, CustomerCreate(customer_id="C-DE", account_name="DE", country="Germany", subsidiary_id="DE"))
    create_customer(db, CustomerCreate(customer_id="C-LEG", account_name="Legacy", country="Spain"))
    db.add(Equipment(customer_id="C-ES", material_no="M-ES", row_hash="h-es"))
    db.add(Equipment(customer_id="C-DE", material_no="M-DE", row_hash="h-de"))
    db.commit()


def test_global_sees_everything(db):
    _seed(db)
    stats = get_stats(db, subsidiary_id=None)
    assert (stats.total_customers, stats.total_equipment) == (3, 2)
    assert stats.total_offers == 0
    assert {c.country: c.count for c in stats.countries} == {"Spain": 2, "Germany": 1}


def test_scoped_sees_only_own_filial(db):
    _seed(db)
    stats = get_stats(db, subsidiary_id="ES")
    assert (stats.total_customers, stats.total_equipment) == (1, 1)
    assert {c.country: c.count for c in stats.countries} == {"Spain": 1}
