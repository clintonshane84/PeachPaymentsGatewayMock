import random
import re
import string
import uuid
from datetime import datetime

import requests
from flask import Blueprint, request, jsonify, redirect, render_template, current_app, url_for, Response

from .generator.payload_generator_factory import PayloadGeneratorFactory
from .models import db, Transaction, User, UserCard, CardRegistration, CheckoutTransactionLink, Checkout
from .utils import generate_connector_tx_id2, generate_connector_tx_id3, generate_short_id, generate_acquirer_ref, \
    generate_reconciliation_id, encrypt_payload

payment_blueprint = Blueprint('payment', __name__)


class PaymentEndpoint:

    # Route to serve the card registration form directly (optional, if you want to access it directly)
    @staticmethod
    @payment_blueprint.route('/register_card_form', methods=['GET'])
    def register_card_form():
        return render_template('register_card.html')

    # Route to serve the payment widget for new card registration
    @staticmethod
    @payment_blueprint.route('/payment_widget', methods=['GET'])
    def payment_widget():
        # Get all query parameters
        query_params = request.args.to_dict()
        return render_template('payment_widget.html', **query_params)

    @staticmethod
    @payment_blueprint.route('/registrations/<token>/payments', methods=['POST'])
    def recurring_payment(token):
        # Validate the token is a 32-character hexadecimal string
        if not re.fullmatch(r'[a-fA-F0-9]{32}', token):
            return jsonify({"error": "Invalid token format"}), 400

        # Retrieve the user through the card token
        user_card = UserCard.query.filter_by(card_token=token).first()
        if not user_card:
            return jsonify({"error": "No user found for the provided token"}), 404

        user = User.query.filter_by(id=user_card.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Retrieve the user's last registered card using the token
        last_registered_card = CardRegistration.query.filter_by(card_token=token).first()
        if not last_registered_card:
            return jsonify({"error": "No registered card found for the provided token"}), 404

        # Handle different content types
        if request.content_type == 'application/json':
            data = request.json
        else:
            data = request.form

        # Extract and validate the required parameters from the request
        entity_id = data.get('entityId')
        amount = data.get('amount')
        currency = data.get('currency', "ZAR")
        payment_type = data.get('paymentType', 'DB')
        standing_instruction_mode = data.get('standingInstruction.mode', 'INITIATED')
        standing_instruction_type = data.get('standingInstruction.type', 'UNSCHEDULED')
        standing_instruction_source = data.get('standingInstruction.source', 'CIT')
        merchant_transaction_id = data.get('merchantTransactionId')
        shopper_result_url = data.get('shopperResultUrl')

        # Check for required parameters
        if not all([entity_id, amount, payment_type, currency, merchant_transaction_id]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Generate unique IDs and other data
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        connector_tx_id1 = str(uuid.uuid4())
        connector_tx_id2 = generate_connector_tx_id2()
        connector_tx_id3 = generate_connector_tx_id3(float(amount))
        reconciliation_id = generate_reconciliation_id()
        ds_transaction_id = str(uuid.uuid4())
        acs_transaction_id = str(uuid.uuid4())
        short_id = generate_short_id()
        payload_id = transaction_id
        shopper_result_url += f"&resourcePath=/v1/payments/{transaction_id}"
        ndc = f"{entity_id}_{payload_id}"
        card_bin = last_registered_card.card_bin
        card_last4_digits = last_registered_card.card_last4_digits
        card_holder = last_registered_card.card_holder
        card_expiry_month = last_registered_card.card_expiry_month
        card_expiry_year = last_registered_card.card_expiry_year
        card_brand = last_registered_card.card_brand
        result_code = "000.200.000"
        result_description = "transaction pending"

        # Create a new transaction record
        new_transaction = Transaction(
            transaction_id=transaction_id,
            registration_id=last_registered_card.card_token,
            payment_type=payment_type,
            payment_brand=card_brand,
            amount=float(amount),
            currency=currency,
            merchant_transaction_id=merchant_transaction_id,
            timestamp=timestamp,
            standing_instruction_mode=standing_instruction_mode,
            standing_instruction_type=standing_instruction_type,
            standing_instruction_source=standing_instruction_source,
            connector_tx_id1=connector_tx_id1,
            connector_tx_id2=connector_tx_id2,
            connector_tx_id3=connector_tx_id3,
            reconciliation_id=reconciliation_id,
            ds_transaction_id=ds_transaction_id,
            acs_transaction_id=acs_transaction_id,
            short_id=short_id,
            payload_id=payload_id,
            ndc=ndc,
            card_bin=card_bin,
            card_last4_digits=card_last4_digits,
            card_holder=card_holder,
            card_expiry_month=card_expiry_month,
            card_expiry_year=card_expiry_year,
            shopper_result_url=shopper_result_url,
            result_code=result_code,
            result_description=result_description
        )
        db.session.add(new_transaction)
        db.session.commit()

        payment_gateway_host = current_app.config.get('PAYMENT_GATEWAY_HOST', 'http://192.168.31.93:5080')

        # Create the mock response
        response = {
            "id": payload_id,
            "paymentType": payment_type,
            "merchantTransactionId": merchant_transaction_id,
            "result": {
                "code": result_code,
                "description": result_description
            },
            "threeDSecure": {
                "challengeIndicator": "04"
            },
            "redirect": {
                "url": f"{payment_gateway_host}/v1/3ds_challenge/{transaction_id}?asyncsource=ACI_3DS_2&type=methodRedirect&cdkForward=true&ndcid={ndc}",
                "parameters": [],
                "preconditions": [
                    {
                        "origin": "iframe#hidden",
                        "waitUntil": "iframe#load",
                        "description": "Hidden iframe post for 3D Secure 2.0",
                        "url": f"{payment_gateway_host}/v1/update_transaction?action=ACI3DS2AccessControlServer&acsRequest=METHOD",
                        "method": "POST",
                        "parameters": [
                            {
                                "name": "threeDSMethodData",
                                "value": "eyJ0aHJlZURTTWV0aG9kTm90aWZpY2F0aW9uVVJMIjoiaHR0cHM6Ly90ZXN0Lm9wcHdhLmNvbS9jb25uZWN0b3JzL2FyX3NpbXVsYXRvci8zZHMyO2pzZXNzaW9uSUQ9MzRERkYxQzY5QTQzQUNGMzY5RTk2NkU5RTc4OEFCNkYudWF0MDEtdm0tY29uMDE_YXN5bmNzb3VyY2U9QUNJXzNEU18yJnR5cGU9bWV0aG9kTm90aWZpY2F0aW9uJm5kY2lkPThhYzdhNGM5N2NiYTFjNGMwMTdjYmNhNjFmOTYwOGU5XzBlZjgzMjdhM2I1MTQ4ODg5N2E4ZWY3MGJhYTc0ZjZiIiwidGhyZWVEU1NlcnZlclRyYW5zSUQiOiJjZDZmOWJjMC1mNDdhLTQwNzUtYjJlYS1jNTI4NWI4NDc4NDcifQ"
                            }
                        ]
                    }
                ]
            },
            "risk": {
                "score": "0"
            },
            "buildNumber": "c7e9cc6e764e4996cd5806410553cc23f9f11d57@2024-05-16 10:52:32 +0000",
            "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S+0000'),
            "ndc": ndc,
            "standingInstruction": {
                "source": standing_instruction_source,
                "type": standing_instruction_type,
                "mode": standing_instruction_mode
            }
        }

        return jsonify(response), 200

    @staticmethod
    @payment_blueprint.route('/cards/register', methods=['POST'])
    def register_card():
        # Extract and validate the required parameters from the request
        data = request.form
        card_number = data.get('cardNumber')
        card_holder = data.get('cardHolder')
        card_expiry_month = data.get('cardExpiryMonth')
        card_expiry_year = data.get('cardExpiryYear')
        card_brand = data.get('cardBrand', 'VISA')  # Default to VISA
        checkout_id = data.get('checkoutId')

        # Check for required parameters
        if not all([card_number, card_holder, card_expiry_month, card_expiry_year, card_brand]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Extract bin and last4Digits from card number
        card_bin, card_last4_digits = CardRegistration.from_card_number(card_number)

        # Create a new card registration record
        new_card_registration = CardRegistration(
            card_number=card_number,
            card_holder=card_holder,
            card_expiry_month=card_expiry_month,
            card_expiry_year=card_expiry_year,
            card_bin=card_bin,
            card_last4_digits=card_last4_digits,
            card_brand=card_brand
        )

        db.session.add(new_card_registration)
        db.session.commit()

        user = User(
            username='test'.join(random.choices(string.digits, k=4))
        )

        db.session.add(user)
        db.session.commit()

        user_card = UserCard(
            user_id=user.id,
            card_token=new_card_registration.card_token,
            card_registration_id=new_card_registration.id
        )

        db.session.add(user_card)
        db.session.commit()

        # Retrieve the related transaction if checkout_id is provided
        transaction = None
        checkout = None
        if checkout_id:
            transaction_link = CheckoutTransactionLink.query.filter_by(checkout_id=checkout_id).first()
            if transaction_link:
                transaction = Transaction.query.filter_by(transaction_id=transaction_link.transaction_id).first()
                checkout = Checkout.query.filter_by(id=checkout_id).first()
                checkout.card_registration_id = new_card_registration.card_token
                transaction.registration_id = new_card_registration.card_token
                transaction.card_bin = card_bin
                transaction.card_holder = card_holder
                transaction.card_last4_digits = card_last4_digits
                transaction.card_expiry_month = card_expiry_month
                transaction.card_expiry_year = card_expiry_year
                transaction.payment_brand = card_brand

                db.session.commit()

        if checkout == None:
            checkout
        ndc = f"{checkout.entity_id}_{transaction.transaction_id}"

        # Create the mock response
        response = {
            "type": "CARD_REGISTRATION",
            "payload": {
                "id": new_card_registration.id,
                "cardBin": card_bin,
                "last4Digits": card_last4_digits,
                "cardHolder": card_holder,
                "cardExpiryMonth": card_expiry_month,
                "cardExpiryYear": card_expiry_year,
                "cardToken": new_card_registration.card_token,
                "cardBrand": card_brand,
                "timestamp": new_card_registration.timestamp.strftime('%Y-%m-%d %H:%M:%S+0000')
            }
        }
        # Redirect to the 3DS challenge
        return redirect(url_for('payment.three_ds_challenge',
                                transaction_id=transaction.transaction_id) + f"?asyncsource=ACI_3DS_2&type=methodRedirect&cdkForward=true&ndcid={ndc}")

    @staticmethod
    @payment_blueprint.route('/3ds_challenge/<transaction_id>', methods=['GET'])
    def three_ds_challenge(transaction_id):

        # Retrieve the transaction to get the shopperResultUrl
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Get all query parameters
        query_params = request.args.to_dict()

        # Render the 3DS challenge HTML form, passing all query parameters
        return render_template('3ds_challenge.html', transaction_id=transaction_id, **query_params)

    @staticmethod
    @payment_blueprint.route('/update_transaction', methods=['POST'])
    def update_transaction():
        outcome = request.form.get('outcome')
        transaction_id = request.form.get('transaction_id')

        # Retrieve the transaction
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Update the transaction status based on the outcome
        if outcome == 'success':
            transaction.result_code = '000.100.110'
            transaction.result_description = 'Request successfully processed in \'Merchant in Integrator Test Mode\''
        elif outcome == 'failure':
            transaction.result_code = '800.100.152'
            transaction.result_description = 'transaction declined by authorization system'
        elif outcome == 'technical_error':
            transaction.result_code = '100.390.112'
            transaction.result_description = 'Technical Error in 3D system'
        else:
            return jsonify({"error": "Invalid outcome"}), 400

        transaction_link = CheckoutTransactionLink.query.filter_by(transaction_id=transaction_id).first()

        if transaction_link:
            checkout = Checkout.query.filter_by(id=transaction_link.checkout_id).first()

            # Retrieve the user's last registered card using the token
            last_registered_card = CardRegistration.query.filter_by(card_token=checkout.card_registration_id).first()
            if not last_registered_card:
                return jsonify({"error": "No registered card found for the user"}), 404

            connector_tx_id1 = str(uuid.uuid4())
            connector_tx_id2 = generate_connector_tx_id2()
            connector_tx_id3 = generate_connector_tx_id3(float(transaction.amount))
            reconciliation_id = generate_reconciliation_id()
            ds_transaction_id = str(uuid.uuid4())
            acs_transaction_id = str(uuid.uuid4())
            short_id = generate_short_id()
            transaction.payload_id = transaction.transaction_id
            transaction.connector_tx_id1 = connector_tx_id1
            transaction.connector_tx_id2 = connector_tx_id2
            transaction.connector_tx_id3 = connector_tx_id3
            transaction.reconciliation_id = reconciliation_id
            transaction.ds_transaction_id = ds_transaction_id
            transaction.acs_transaction_id = acs_transaction_id
            transaction.short_id = short_id

        db.session.commit()

        # Create the payload generator
        payload_generator = PayloadGeneratorFactory.get_payload_generator('card_register', transaction)
        # Generate the payload for the callback
        payload = payload_generator.generate_payload()
        # Send the webhook to the merchant's server
        response = PaymentEndpoint.send_webhook(payload)

        if response.status_code == 200:
            message = "Transaction processed successfully"
        else:
            message = "Transaction failed to process"

        # Redirect the user to the shopperResultUrl
        if transaction.shopper_result_url:
            return redirect(transaction.shopper_result_url)
        return jsonify({"message": message}), 200

    @staticmethod
    @payment_blueprint.route('/payments/<transaction_id>', methods=['GET'])
    def query_payment(transaction_id):
        # Retrieve the transaction
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()

        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Create the response payload using the transaction data
        response = {
            "type": "PAYMENT",
            "id": transaction.transaction_id,
            "registrationId": transaction.registration_id,
            "paymentType": transaction.payment_type,
            "paymentBrand": transaction.payment_brand,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "merchantTransactionId": transaction.merchant_transaction_id,
            "result": {
                "code": transaction.result_code,
                "description": transaction.result_description
            },
            "card": {
                "bin": transaction.card_bin,
                "last4Digits": transaction.card_last4_digits,
                "holder": transaction.card_holder,
                "expiryMonth": transaction.card_expiry_month,
                "expiryYear": transaction.card_expiry_year,
                "binCountry": "ZA"
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

        return jsonify(response), 200

    @staticmethod
    @payment_blueprint.route('/checkouts', methods=['POST'])
    def create_checkout():

        # Handle different content types
        if request.content_type == 'application/json':
            data = request.json
        else:
            data = request.form

        entity_id = data.get('entityId')
        amount = data.get('amount')
        currency = data.get('currency')
        payment_type = data.get('paymentType')
        merchant_transaction_id = data.get('merchantTransactionId', '')
        shopper_result_url = current_app.config.get('SHOPPER_RESULT_URL',
                                                    'http://localhost/m/web.php?SN=peachReturnShopper&params=')
        standing_instruction_mode = data.get('standingInstruction.mode', 'INITIATED')
        standing_instruction_type = data.get('standingInstruction.type', 'UNSCHEDULED')
        standing_instruction_source = data.get('standingInstruction.source', 'CIT')

        # Validate required parameters
        if not all([entity_id, amount, currency, payment_type]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Generate response data
        checkout_id = str(uuid.uuid4()).replace("-", "").upper()
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S+0000')

        # Create a new checkout record
        new_checkout = Checkout(
            id=checkout_id,
            entity_id=entity_id,
            amount=float(amount),
            currency=currency,
            payment_type=payment_type,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_checkout)
        db.session.commit()

        # Create a new transaction record with pending status
        new_transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            payment_type=payment_type,
            payment_brand="",
            amount=float(amount),
            currency=currency,
            result_code="000.200.000",
            result_description="transaction pending",
            timestamp=datetime.utcnow(),
            shopper_result_url=shopper_result_url,
            standing_instruction_type=standing_instruction_type,
            standing_instruction_mode=standing_instruction_mode,
            standing_instruction_source=standing_instruction_source,
            merchant_transaction_id=merchant_transaction_id
        )
        db.session.add(new_transaction)
        db.session.commit()

        # Create the link between checkout and transaction
        checkout_transaction_link = CheckoutTransactionLink(
            checkout_id=checkout_id,
            transaction_id=new_transaction.transaction_id
        )
        db.session.add(checkout_transaction_link)
        db.session.commit()

        response_data = {
            "result": {
                "code": "000.200.100",
                "description": "successfully created checkout"
            },
            "buildNumber": "17b6f0d02db9a254e0f55fcd2b0d5645aa471480@2024-05-27 14:08:57 +0000",
            "timestamp": timestamp,
            "ndc": checkout_id + ".uat01-vm-tx02",
            "id": checkout_id + ".uat01-vm-tx02"
        }

        return jsonify(response_data), 200

    @staticmethod
    @payment_blueprint.route('/payments/<transaction_id>', methods=['POST'])
    def payments(transaction_id):
        # Retrieve the transaction
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()

        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Handle different content types
        if request.content_type == 'application/json':
            data = request.json
        else:
            data = request.form

        outcome = request.form.get('outcome', 'success')
        result_code = '000.100.110'
        result_description = 'Request successfully processed in \'Merchant in Integrator Test Mode\''

        # Update the transaction status based on the outcome
        if outcome == 'failure':
            result_code = '800.100.152'
            result_description = 'transaction declined by authorization system'
        elif outcome == 'technical_error':
            transaction.result_code = '100.390.112'
            result_description = 'Technical Error in 3D system'
        else:
            return jsonify({"error": "Invalid outcome"}), 400

        # Extract and validate the required parameters from the request
        entity_id = data.get('entityId')
        amount = data.get('amount')
        currency = data.get('currency', "ZAR")
        payment_type = data.get('paymentType', 'DB')
        standing_instruction_mode = data.get('standingInstruction.mode', 'INITIATED')
        standing_instruction_type = data.get('standingInstruction.type', 'UNSCHEDULED')
        standing_instruction_source = data.get('standingInstruction.source', 'CIT')
        merchant_transaction_id = data.get('merchantTransactionId')
        shopper_result_url = data.get('shopperResultUrl', '')

        # Check for required parameters
        if not all([entity_id, amount, payment_type, currency, merchant_transaction_id]):
            return jsonify({"error": "Missing required parameters"}), 400

        last_registered_card = CardRegistration()
        transaction_link = CheckoutTransactionLink.query.filter_by(transaction_id=transaction_id).first()

        if transaction_link:
            checkout = Checkout.query.filter_by(id=transaction_link.checkout_id).first()

            # Retrieve the user's last registered card using the token
            last_registered_card = CardRegistration.query.filter_by(card_token=checkout.card_registration_id).first()
            if not last_registered_card:
                return jsonify({"error": "No registered card found for the user"}), 404

        # Generate unique IDs and other data
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        connector_tx_id1 = str(uuid.uuid4())
        connector_tx_id2 = generate_connector_tx_id2()
        connector_tx_id3 = generate_connector_tx_id3(float(amount))
        reconciliation_id = generate_reconciliation_id()
        ds_transaction_id = str(uuid.uuid4())
        acs_transaction_id = str(uuid.uuid4())
        short_id = generate_short_id()
        payload_id = transaction_id
        ndc = f"{entity_id}_{payload_id}"
        card_bin = last_registered_card.card_bin
        card_last4_digits = last_registered_card.card_last4_digits
        card_holder = last_registered_card.card_holder
        card_expiry_month = last_registered_card.card_expiry_month
        card_expiry_year = last_registered_card.card_expiry_year
        card_brand = last_registered_card.card_brand

        # Create a new transaction record
        new_transaction = Transaction(
            transaction_id=transaction_id,
            registration_id=last_registered_card.id,
            payment_type=payment_type,
            payment_brand=card_brand,
            amount=float(amount),
            currency=currency,
            merchant_transaction_id=merchant_transaction_id,
            timestamp=timestamp,
            standing_instruction_mode=standing_instruction_mode,
            standing_instruction_type=standing_instruction_type,
            standing_instruction_source=standing_instruction_source,
            connector_tx_id1=connector_tx_id1,
            connector_tx_id2=connector_tx_id2,
            connector_tx_id3=connector_tx_id3,
            reconciliation_id=reconciliation_id,
            ds_transaction_id=ds_transaction_id,
            acs_transaction_id=acs_transaction_id,
            short_id=short_id,
            payload_id=payload_id,
            ndc=ndc,
            card_bin=card_bin,
            card_last4_digits=card_last4_digits,
            card_holder=card_holder,
            card_expiry_month=card_expiry_month,
            card_expiry_year=card_expiry_year,
            shopper_result_url=shopper_result_url,
            result_code=result_code,
            result_description=result_description
        )
        db.session.add(new_transaction)
        db.session.commit()

        # Create the payload generator
        payload_generator = PayloadGeneratorFactory.get_payload_generator('recurring_payment', transaction, data)
        # Generate the payload for the callback
        payload = payload_generator.generate_payload()

        if payment_type in ["RV", "RF"]:
            payload['paymentMethod'] = payment_type
            payload['referenceId'] = transaction_id
            payload['resultDetails']['AcquirerReference'] = generate_acquirer_ref()

        # Send the callback to the configured URL
        PaymentEndpoint.send_webhook(payload)

        return jsonify(payload), 200

    @staticmethod
    def send_webhook(payload) -> Response:
        # Encryption key (should be securely stored and retrieved in production)
        key = current_app.config.get('ENCRYPTION_KEY')
        key = bytes.fromhex(key)

        # Encrypt the payload
        encrypted_payload, iv, auth_tag = encrypt_payload(payload, key)

        response_payload = {
            "encryptedBody": encrypted_payload
        }

        headers = {
            'X-Initialization-Vector': iv,
            'X-Authentication-Tag': auth_tag
        }

        # Send the callback to the configured URL
        webhook_url = current_app.config.get('WEBHOOK_URL')
        response = requests.post(webhook_url, json=response_payload, headers=headers, verify=False)
        return response
