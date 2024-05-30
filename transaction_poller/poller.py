import time
from .services import TransactionService

class Poller:
    def __init__(self, transaction_service):
        self.transaction_service = transaction_service

    def poll(self):
        while True:
            transactions = self.transaction_service.transaction_repository.get_pending_transactions()
            for transaction in transactions:
                self.transaction_service.process_transaction(transaction)
            time.sleep(5)  # Polling interval
