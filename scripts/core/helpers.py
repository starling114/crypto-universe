import random
from utils import SECRETS, CONFIGS, int_to_wei, wei_to_int, round_number, ExecutionError, logger


def transaction_data(web3, from_address, to_address=None, data=None, value=None):
    from_address = web3.to_checksum_address(from_address)

    tx_data = {
        "chainId": web3.eth.chain_id,
        "nonce": web3.eth.get_transaction_count(from_address),
        "from": from_address,
        **gas_fees(web3),
    }

    if to_address is not None:
        tx_data["to"] = web3.to_checksum_address(to_address)

    if value is not None:
        tx_data["value"] = value

    if data is not None:
        tx_data["data"] = data

    return tx_data


def transactions_count(web3, wallet_address):
    return int(web3.eth.get_transaction_count(web3.to_checksum_address(wallet_address)))


def gas_fees(web3):
    base_fee = web3.eth.gas_price
    max_priority_fee_per_gas = web3.eth.max_priority_fee

    multiplier = 1.2
    if web3.eth.chain_id == CONFIGS["chains"]["berachain"]["chain_id"]:
        multiplier = 1.5
    elif web3.eth.chain_id == CONFIGS["chains"]["ethereum"]["chain_id"]:
        multiplier = 1.1

    return {
        "maxPriorityFeePerGas": max_priority_fee_per_gas,
        "maxFeePerGas": int((base_fee + max_priority_fee_per_gas) * multiplier),
    }


def estimate_gas(web3, tx_data):
    gas = web3.eth.estimate_gas(tx_data)

    multiplier = 1.2
    if web3.eth.chain_id == CONFIGS["chains"]["berachain"]["chain_id"]:
        multiplier = 1.5
    elif web3.eth.chain_id == CONFIGS["chains"]["ethereum"]["chain_id"]:
        multiplier = 1.1

    return int(gas * multiplier)


def token_allowance(token, spender_address, wallet_address):
    return token.contract.functions.allowance(wallet_address, spender_address).call()


def approve_token(web3, token, amount, spender_address, wallet_address, private_key):
    if token.is_native():
        return True

    allowance = token_allowance(token, spender_address, wallet_address)

    if allowance >= amount:
        return True

    data = token.contract.encodeABI("approve", args=(spender_address, amount))
    tx_data = transaction_data(web3, from_address=wallet_address, to_address=token.address, data=data)
    tx_hash = send_transaction(web3, tx_data, private_key)

    return verify_transaction(web3, tx_hash)


def send_transaction(web3, tx_data, private_key):
    tx_data["gas"] = estimate_gas(web3, tx_data)

    signed_tx = web3.eth.account.sign_transaction(tx_data, private_key)

    if hasattr(signed_tx, "raw_transaction"):
        raw_tx = signed_tx.raw_transaction
    elif hasattr(signed_tx, "rawTransaction"):
        raw_tx = signed_tx.rawTransaction
    else:
        raise ExecutionError("SignedTransaction does not contain raw_transaction or rawTransaction.")

    raw_tx_hash = web3.eth.send_raw_transaction(raw_tx)

    return web3.to_hex(raw_tx_hash)


def verify_transaction(web3, tx_hash):
    response = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=int(2 * 60))

    if "status" in response and response["status"] == 1:
        return True
    else:
        return False


# Support functions


def get_private_key(web3, address, secrets=None):
    private_key = None

    if secrets is not None:
        private_key = secrets["private_keys"].get(address, None)

    if private_key is None:
        private_key = SECRETS["private_keys"].get(address, None)

    if private_key is None:
        raise ExecutionError("Private key was not found")

    if web3.eth.account.from_key(private_key).address != web3.to_checksum_address(address):
        raise ExecutionError("Wrong private key for address")

    return private_key


def get_transaction_link(chain, tx_hash):
    return f"{chain.scan}/tx/{tx_hash}"


def zip_to_objects(objects, to_zip):
    return {object: value for object, value in zip(objects, to_zip)}


def prettify_seconds(seconds):
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


def prettify_number(value):
    rounded_number = round_number(float(value))
    number_str = str(rounded_number)

    if "e" not in number_str and "E" not in number_str:
        return number_str

    number = float(number_str)
    exponent_value = int(number_str[number_str.index("e") + 1 :])

    return f"{number:.{max(0, -exponent_value)}f}"


# Calculate helper functions


def calculate_token_balance(web3, wallet_address, token, check_balance=True):
    if token.is_native():
        balance = web3.eth.get_balance(web3.to_checksum_address(wallet_address))
    else:
        balance = token.contract.functions.balanceOf(web3.to_checksum_address(wallet_address)).call()

    if check_balance and balance <= 0:
        raise ExecutionError("Not enough balance. Balance <= 0")

    return int(balance)


def calculate_base_amount(balance, amount, leave_balance, leave_balance_amount):
    calculated_amount = 0

    if leave_balance:
        if balance <= int_to_wei(float(leave_balance_amount)):
            raise ExecutionError(
                f"Not enough balance. Balance <= Leave Balance Amount ({prettify_number(wei_to_int(balance))} <= {leave_balance_amount})"
            )
        else:
            calculated_amount = balance - int_to_wei(float(leave_balance_amount))
    else:
        calculated_amount = int_to_wei(float(amount))

    return calculated_amount


def execute_amount_validations(
    balance,
    amount,
    min_transaction_amount=0.0000001,
    max_transaction_amount=1000,
):
    min_amount = int_to_wei(min_transaction_amount)
    max_amount = int_to_wei(max_transaction_amount)
    if balance < amount:
        raise ExecutionError(
            f"Not enough balance. Balance < Amount ({prettify_number(wei_to_int(balance))} < {prettify_number(wei_to_int(amount))})"
        )

    if amount < min_amount:
        raise ExecutionError(
            f"Amount < Min transaction amount ({prettify_number(wei_to_int(amount))} < {prettify_number(wei_to_int(min_amount))})"
        )

    if amount > max_amount:
        raise ExecutionError(
            f"Amount > Max transaction amount ({prettify_number(wei_to_int(amount))} > {prettify_number(wei_to_int(max_amount))})"
        )
