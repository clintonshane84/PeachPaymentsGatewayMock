import random
import string

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
