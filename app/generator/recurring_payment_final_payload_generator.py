from typing import Dict, Any

from werkzeug.sansio.request import Request

import app
from .payload_generator_interface import PayloadGeneratorInterface
from .. import utils
from ..models import Transaction


class RecurringPaymentFinalPayloadGenerator(PayloadGeneratorInterface):

    def __init__(self, transaction: Transaction, data: Dict[str, Any] = None):
        if data is None:
            data = {}
        self.transaction = transaction
        self.data = data

    def generate_payload(self) -> Dict:
        # Implement the payload generation logic for recurring payment
        transaction = self.transaction
        return {
            "type": "PAYMENT",
            "id": transaction.transaction_id,
            "registrationId": transaction.registration_id,
            "paymentType": transaction.payment_type,
            "paymentBrand": transaction.payment_brand,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "merchantTransactionId": transaction.merchant_transaction_id,
            "result": {
                "avsResponse": "F",
                "code": transaction.result_code,
                "description": transaction.result_description
            },
            "card": {
                "bin": transaction.card_bin,
                "last4Digits": transaction.card_last4_digits,
                "holder": transaction.card_holder,
                "expiryMonth": transaction.card_expiry_month,
                "expiryYear": transaction.card_expiry_year
            },
            "threeDSecure": {
                "eci": "05",
                "verificationId": "MTIzNDU2Nzg5MDEyMzQ1Njc4OTA=",
                "version": "2.2.0",
                "challengeMandatedIndicator": "N",
                "cardHolderInfo": "",
                "authType": "01",
                "flow": "challenge",
                "authenticationStatus": "Y",
                "dsTransactionId": transaction.ds_transaction_id,
                "acsTransactionId": transaction.acs_transaction_id
            },
            "resultDetails": {
                "AuthCode": "012345",
                "AcquirerResponse": "00",
                "ConnectorTxID1": transaction.connector_tx_id1,
                "ConnectorTxID2": transaction.connector_tx_id2,
                "ConnectorTxID3": transaction.connector_tx_id3,
                "reconciliationId": transaction.reconciliation_id,
                "CardholderInitiatedTransactionID": "123456789012345"
            },
            "authentication": {
                "entityId": self.data.get('entityId')
            },
            "buildNumber": utils.generate_build_number(),
            "timestamp": transaction.timestamp.isoformat(),
            "ndc": transaction.ndc,
            "standingInstruction": {
                "mode": transaction.standing_instruction_mode,
                "type": transaction.standing_instruction_type,
                "source": transaction.standing_instruction_source
            },
            "risk": {
                "score": "0"
            },
            "source": "OPP",
            "paymentMethod": "CC",
            "shortId": transaction.short_id
        }
