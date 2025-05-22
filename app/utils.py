import random
import string
from datetime import datetime

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import base64
import json

from flask import current_app


def generate_connector_tx_id2():
    part1 = ''.join(random.choices(string.digits, k=6))
    part2 = ''.join(random.choices(string.digits, k=12))
    part3 = part2  # Same as part2
    part4 = "CIT"
    part5 = "ECOMMERCE"
    part6 = ""
    part7 = ""
    part8 = ""

    connector_tx_id2 = f"{part1}|{part2}|{part3}|{part4}|{part5}|{part6}|{part7}|{part8}"
    return connector_tx_id2


def generate_connector_tx_id3(order_amount):
    part1 = ''.join(random.choices(string.digits, k=6))
    part2 = ''.join(random.choices(string.digits, k=2))
    part3 = ''.join(random.choices(string.digits, k=4))
    part4 = ''.join(random.choices(string.digits, k=6))
    part5 = ''.join(random.choices(string.digits, k=15))
    part6 = ''.join(random.choices(string.digits, k=15))
    part7 = f"{order_amount:.2f}"

    connector_tx_id3 = f"{part1}|{part2}|{part3}|{part4}|{part5}|{part6}|{part7}"
    return connector_tx_id3


def generate_short_id():
    part1 = ''.join(random.choices(string.digits, k=4))
    part2 = ''.join(random.choices(string.digits, k=4))
    part3 = ''.join(random.choices(string.digits, k=4))

    tmp_id = f"{part1}.{part2}.{part3}"
    return tmp_id


def generate_acquirer_ref():
    part1 = ''.join(random.choices(string.digits, k=5))
    part2 = ''.join(random.choices(string.digits, k=8))

    tmp_id = f"{part1}:{part2}"
    return tmp_id


def generate_reconciliation_id():
    part1 = ''.join(random.choices(string.digits, k=4))
    part2 = ''.join(random.choices(string.digits, k=12))
    part3 = ''.join(random.choices(string.digits, k=10))

    tmp_id = f"{part1}:{part2}:{part3}"
    return tmp_id


def generate_build_number():
    # Generate 40 random hexadecimal characters
    random_chars = ''.join(random.choices(string.hexdigits.lower(), k=40))

    # Get the current date-time in the specified format
    current_datetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S +0000')

    # Combine the random characters and the date-time to form the build number
    build_number = f"{random_chars}@{current_datetime}"

    return build_number


def encrypt_payload(payload, key):
    # Convert payload to JSON string
    payload_str = json.dumps(payload)

    # Generate IV (12 bytes for GCM mode)
    iv = os.urandom(12)

    # Create AES-GCM cipher
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    # Encrypt the payload
    cipher_text = encryptor.update(payload_str.encode()) + encryptor.finalize()
    auth_tag = encryptor.tag

    # Encode the encrypted payload, IV, and auth tag in uppercase hexadecimal
    encrypted_payload = cipher_text.hex().upper()
    iv = iv.hex().upper()
    auth_tag = auth_tag.hex().upper()

    return encrypted_payload, iv, auth_tag
