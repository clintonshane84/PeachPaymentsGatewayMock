import sys
import os

# Append the root directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db, config
from transaction_poller.repositories import TransactionRepository
from transaction_poller.services import TransactionService
from transaction_poller.poller import Poller

app = create_app('dev')

def main():
    with app.app_context():
        transaction_repository = TransactionRepository(db)
        transaction_service = TransactionService(transaction_repository)
        poller = Poller(transaction_service)

        poller.poll()

if __name__ == "__main__":
    main()
