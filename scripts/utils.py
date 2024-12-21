import os
import json
import sys
import requests
import random
import traceback
import time
from loguru import logger

NULL_TOKEN_ADDRESS = "0x0000000000000000000000000000000000000000"
NATIVE_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


def debug_mode():
    return os.getenv("DEBUG") == "true"


logger.remove()
logger.level("INFO", color="<bold><cyan>")
logger.level("WARNING", color="<bold><yellow>")
logger.level("DEBUG", color="<bold><blue>")
level = "DEBUG" if debug_mode() and False else "INFO"
format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}"
logger.add(sys.stdout, colorize=True, format=format, level=level)


class ExecutionError(Exception):
    pass


def load_json(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r") as file:
        return json.load(file)


def humanify_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_str = []
    if hours > 0:
        time_str.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        time_str.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not time_str:
        time_str.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return ", ".join(time_str)


def round_number(number, precision=5):
    return round(number, precision)


def humanify_number(value):
    rounded_number = round_number(float(value))
    number_str = str(rounded_number)

    if "e" not in number_str and "E" not in number_str:
        return number_str

    number = float(number_str)
    exponent_value = int(number_str[number_str.index("e") + 1 :])

    return f"{number:.{max(0, -exponent_value)}f}"


def int_to_wei(qty, decimals=18):
    return int(qty * int("".join(["1"] + ["0"] * decimals)))


def wei_to_int(qty, decimals=18):
    return qty / int("".join((["1"] + ["0"] * decimals)))


def post_call(url, data=None, json=None, headers=None):
    response = requests.post(url, data=data, json=json, headers=headers, verify=True)
    response.raise_for_status()

    return response.json()


def get_call(url, params=None, headers=None):
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    return response.json()


def get_balance(web3, wallet_address, contract=None):
    if contract:
        balance = contract.functions.balanceOf(web3.to_checksum_address(wallet_address)).call()
    else:
        balance = web3.eth.get_balance(web3.to_checksum_address(wallet_address))

    return int(balance)


def get_transactions_count(web3, wallet_address):
    count = web3.eth.get_transaction_count(web3.to_checksum_address(wallet_address))

    return int(count)


def get_gas_price(web3):
    # Do not multiply gas price for mainnet
    if web3.eth.chain_id == 1:
        return int(web3.eth.gas_price)
    else:
        return int(web3.eth.gas_price * 1.2)


def get_gas_limit(web3, contract_txn):
    gas_limit = web3.eth.estimate_gas(contract_txn)

    multiplier = [1.1, 1.2]
    return int(gas_limit * random.uniform(multiplier[0], multiplier[1]))


def sign_tx(web3, contract_txn, private_key):
    signed_tx = web3.eth.account.sign_transaction(contract_txn, private_key)

    if hasattr(signed_tx, "raw_transaction"):
        raw_tx = signed_tx.raw_transaction
    elif hasattr(signed_tx, "rawTransaction"):
        raw_tx = signed_tx.rawTransaction
    else:
        raise AttributeError("SignedTransaction does not contain raw_transaction or rawTransaction.")

    raw_tx_hash = web3.eth.send_raw_transaction(raw_tx)
    tx_hash = web3.to_hex(raw_tx_hash)

    return tx_hash


def zip_to_addresses(addresses, to_zip):
    return {address: amount for address, amount in zip(addresses, to_zip)}


def get_private_key(web3, settings, address):
    private_key = settings["private_keys"][address]

    if web3.eth.account.from_key(private_key).address != web3.to_checksum_address(address):
        raise ExecutionError("Wrong private key for address")

    return private_key


def get_tx_link(scan, tx_hash):
    return f"{scan}/tx/{tx_hash}"


def wait_tx_completion(web3, tx_hash):
    try:
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=int(2 * 60))

        if tx_receipt["status"] == 1:
            return True
        else:
            return False
    except TimeoutError:
        return False


def get_token_data(web3, token_address):
    abi = load_json("../erc20abi.json")

    token_contract = web3.eth.contract(address=web3.to_checksum_address(token_address), abi=abi)
    decimals = token_contract.functions.decimals().call()
    symbol = token_contract.functions.symbol().call()

    return web3.to_checksum_address(token_address), token_contract, decimals, symbol


def log_error(error, prefix=""):
    formatted_prefix = f"{prefix} | " if prefix != "" else ""

    if debug_mode():
        error_str = f"\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}"
    else:
        tb_list = traceback.extract_tb(error.__traceback__)
        filename, lineno, funcname, _ = tb_list[-1]
        error_str = f" {filename}:{lineno}, function: {funcname}"

    logger.error(f"{formatted_prefix}{type(error).__name__}: {str(error)}{error_str}")


def sleep(delay, max_delay=None):
    if max_delay is not None:
        delay = random.uniform(delay, max_delay)

    time.sleep(delay)
