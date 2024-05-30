import unittest
from unittest.mock import Mock
from transaction_poller.services import TransactionService
from app.models import Transaction

class TestTransactionService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = Mock()
        self.transaction_service = TransactionService(self.mock_repository)

    def test_process_transaction_success(self):
        transaction = Transaction(
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
            ndc="ndc"
        )

        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            self.transaction_service.process_transaction(transaction)
            self.mock_repository.update_transaction_status.assert_called_with(
                "test_id", "completed", "Transaction processed successfully"
            )

    def test_process_transaction_failure(self):
        transaction = Transaction(
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
            ndc="ndc"
        )

        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            self.transaction_service.process_transaction(transaction)
            self.mock_repository.update_transaction_status.assert_called_with(
                "test_id", "failed", "Transaction failed to process"
            )

if __name__ == '__main__':
    unittest.main()
