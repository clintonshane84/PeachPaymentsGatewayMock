from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    registration_id = db.Column(db.String(50), nullable=True)
    payment_type = db.Column(db.String(10), nullable=False)
    payment_brand = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    merchant_transaction_id = db.Column(db.String(50), nullable=False)
    result_code = db.Column(db.String(10), nullable=False)
    result_description = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    standing_instruction_mode = db.Column(db.String(50), nullable=True)
    standing_instruction_type = db.Column(db.String(50), nullable=True)
    standing_instruction_source = db.Column(db.String(50), nullable=True)
    connector_tx_id1 = db.Column(db.String(50), nullable=True)
    connector_tx_id2 = db.Column(db.String(50), nullable=True)
    connector_tx_id3 = db.Column(db.String(50), nullable=True)
    reconciliation_id = db.Column(db.String(50), nullable=True)
    ds_transaction_id = db.Column(db.String(50), nullable=True)
    acs_transaction_id = db.Column(db.String(50), nullable=True)
    short_id = db.Column(db.String(20), nullable=True)
    payload_id = db.Column(db.String(50), nullable=True)
    ndc = db.Column(db.String(50), nullable=True)
    card_bin = db.Column(db.String(10), nullable=True)
    card_last4_digits = db.Column(db.String(4), nullable=True)
    card_holder = db.Column(db.String(50), nullable=True)
    card_expiry_month = db.Column(db.String(2), nullable=True)
    card_expiry_year = db.Column(db.String(2), nullable=True)
    shopper_result_url = db.Column(db.String(255), nullable=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    @classmethod
    def create_test_user(cls):
        # Create a test user
        test_user = User(username='testuser')
        db.session.add(test_user)
        db.session.commit()

        # Create a test card registration
        test_card_registration = CardRegistration(
            card_number='4242424242424242',
            card_holder='Test User',
            card_expiry_month='12',
            card_expiry_year='2025',
            card_bin='424242',
            card_last4_digits='4242',
            card_brand='VISA'
        )
        db.session.add(test_card_registration)
        db.session.commit()

        # Link the test user with the test card
        user_card = UserCard(
            user_id=test_user.id,
            card_registration_id=test_card_registration.id,
            card_token=test_card_registration.card_token
        )
        db.session.add(user_card)
        db.session.commit()

        return test_user, test_card_registration, user_card


class UserCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_registration_id = db.Column(db.Integer, db.ForeignKey('card_registration.id'), nullable=False)
    card_token = db.Column(db.String(32), nullable=False)
    user = db.relationship('User', backref=db.backref('user_cards', lazy=True))
    card_registration = db.relationship('CardRegistration', backref=db.backref('user_cards', lazy=True))

    def __repr__(self):
        return f'<UserCard {self.user_id}-{self.card_registration_id}>'


class CardRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(16), nullable=False)
    card_holder = db.Column(db.String(80), nullable=False)
    card_expiry_month = db.Column(db.String(2), nullable=False)
    card_expiry_year = db.Column(db.String(4), nullable=False)
    card_bin = db.Column(db.String(6), nullable=False)
    card_last4_digits = db.Column(db.String(4), nullable=False)
    card_token = db.Column(db.String(32), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    card_brand = db.Column(db.String(20), nullable=False, default='VISA')
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<CardRegistration {self.card_bin}****{self.card_last4_digits}>'

    @staticmethod
    def from_card_number(card_number):
        return card_number[:6], card_number[-4:]


class Checkout(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    entity_id = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    payment_type = db.Column(db.String(2), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    card_registration_id = db.Column(db.String(50), db.ForeignKey('card_registration.card_token'), nullable=True)


class CheckoutTransactionLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checkout_id = db.Column(db.String(50), db.ForeignKey('checkout.id'), nullable=False)
    transaction_id = db.Column(db.String(50), db.ForeignKey('transaction.transaction_id'), nullable=False)
