import unittest
from app import create_app, db
from app.models import Transaction
from transaction_poller.repositories import TransactionRepository

class TestTransactionRepository(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.transaction_repository = TransactionRepository(db)
        self.sample_transaction = Transaction(
            transaction_id="test_id",
            registration_id="reg_id",
            payment_type="DB",
            payment_brand="VISA",
            amount=100.0,
            currency="ZAR",
            merchant_transaction_id="merch_id",
            card_bin="420000",
            card_last4_digits="1234",
            card_holder="John Doe",
            card_expiry_month="12",
            card_expiry_year="2025",
            connector_tx_id1="tx_id1",
            connector_tx_id2="tx_id2",
            connector_tx_id3="tx_id3",
            reconciliation_id="rec_id",
            ds_transaction_id="ds_id",
            acs_transaction_id="acs_id",
            short_id="short_id",
            payload_id="payload_id",
            ndc="ndc",
            result_code="000.200.000"
        )
        db.session.add(self.sample_transaction)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_pending_transactions(self):
        transactions = self.transaction_repository.get_pending_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].transaction_id, "test_id")

    def test_update_transaction_status(self):
        self.transaction_repository.update_transaction_status("test_id", "completed", "Test description")
        transaction = Transaction.query.filter_by(transaction_id="test_id").first()
        self.assertEqual(transaction.result_code, "completed")
        self.assertEqual(transaction.result_description, "Test description")

if __name__ == '__main__':
    unittest.main()
