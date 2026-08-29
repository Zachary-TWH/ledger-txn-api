# Background tasks run by Celery workers, separate from the API process

from .celery_app import celery_app
from .database import SessionLocal
from . import models
from sqlalchemy import func
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def reconcile_all_accounts_task():
    db = SessionLocal()
    try:
        accounts = db.query(models.Account).all()
        for account in accounts:
            total_credits = db.query(func.sum(models.LedgerEntry.amount)).filter(
                models.LedgerEntry.account_id == account.id,
                models.LedgerEntry.entry_type == models.EntryType.CREDIT
            ).scalar() or Decimal(0)

            total_debits = db.query(func.sum(models.LedgerEntry.amount)).filter(
                models.LedgerEntry.account_id == account.id,
                models.LedgerEntry.entry_type == models.EntryType.DEBIT
            ).scalar() or Decimal(0)

            computed_balance = total_credits - total_debits

            if computed_balance != account.balance:
                logger.warning(f"RECONCILIATION ALERT: account {account.id} ({account.owner_name}) "
                      f"stored={account.balance}, computed={computed_balance}")
            else:
                logger.info(f"RECONCILIATION OK: account {account.id} ({account.owner_name}) "
                      f"balance={account.balance}")
    finally:
        db.close()