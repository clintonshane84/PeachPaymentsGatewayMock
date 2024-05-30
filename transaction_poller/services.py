import requests


class TransactionService:
    def __init__(self, transaction_repository):
        self.transaction_repository = transaction_repository

    def process_transaction(self, transaction):
        payload = {
            "type": "PAYMENT",
            "payload": {
                "id": transaction.transaction_id,
                "registrationId": transaction.registration_id,
                "paymentType": transaction.payment_type,
                "paymentBrand": transaction.payment_brand,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "merchantTransactionId": transaction.merchant_transaction_id,
                "result": {
                    "code": "000.100.110",
                    "description": "Request successfully processed in 'Merchant in Integrator Test Mode'"
                },
                "card": {
                    "bin": transaction.card_bin,
                    "last4Digits": transaction.card_last4_digits,
                    "holder": transaction.card_holder,
                    "expiryMonth": transaction.card_expiry_month,
                    "expiryYear": transaction.card_expiry_year
                },
                "threeDSecure": {
                    "dsTransactionId": transaction.ds_transaction_id,
                    "acsTransactionId": transaction.acs_transaction_id
                },
                "resultDetails": {
                    "ConnectorTxID1": transaction.connector_tx_id1,
                    "ConnectorTxID2": transaction.connector_tx_id2,
                    "ConnectorTxID3": transaction.connector_tx_id3,
                    "reconciliationId": transaction.reconciliation_id
                },
                "timestamp": transaction.timestamp.isoformat(),
                "ndc": transaction.ndc,
                "shortId": transaction.short_id,
                "standingInstruction": {
                    "mode": transaction.standing_instruction_mode,
                    "type": transaction.standing_instruction_type,
                    "source": transaction.standing_instruction_source
                }
            }
        }

        webhook_url = current_app.config.get('WEBHOOK_URL')
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            self.transaction_repository.update_transaction_status(transaction.transaction_id, "completed",
                                                                  "Transaction processed successfully")
        else:
            self.transaction_repository.update_transaction_status(transaction.transaction_id, "failed",
                                                                  "Transaction failed to process")
