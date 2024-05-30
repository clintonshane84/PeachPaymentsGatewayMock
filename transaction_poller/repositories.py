from app.models import Transaction

class TransactionRepository:
    def __init__(self, db):
        self.db = db

    def get_pending_transactions(self):
        return Transaction.query.filter_by(result_code="000.200.000").all()

    def update_transaction_status(self, transaction_id, status, description):
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
        if transaction:
            transaction.result_code = status
            transaction.result_description = description
            self.db.session.commit()
