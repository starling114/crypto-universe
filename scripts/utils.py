import os
import json
import sys
import importlib
import requests
import random
import traceback
import time
from loguru import logger

NULL_TOKEN_ADDRESS = "0x0000000000000000000000000000000000000000"


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


SECRETS = load_json("../backend/modules/crypto_universe/secrets.json")
CONFIGS = load_json("../configs.json")
ERC20_ABI = load_json("../erc20abi.json")


def round_number(number, precision=5):
    return round(number, precision)


def int_to_wei(qty, decimals=18):
    return int(qty * int("".join(["1"] + ["0"] * decimals)))


def wei_to_int(qty, decimals=18):
    return qty / int("".join((["1"] + ["0"] * decimals)))


def post_call(url, json=None, headers=None):
    response = requests.post(url, json=json, headers=headers, verify=True)
    response.raise_for_status()

    return response.json()


def get_call(url, params=None, headers=None):
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    return response.json()


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


def import_premium_module(file, name):
    try:
        module = importlib.import_module(f"modules.premium.{file}")
    except ImportError:
        try:
            module = importlib.import_module(f"modules.premium.private.{file}")
        except ImportError:
            return None

    return getattr(module, name)


def run_module(aaarg, modules):
    module = modules.get(aaarg, None)
    if module:
        module.run()
    else:
        logger.error(f"Invalid module choice: {aaarg}")


def run_premium_module(aaarg, modules):
    module = modules.get(aaarg, None)
    if module:
        location = "/".join(aaarg.split("-"))
        instructions = load_json(f"modules/{location}/instructions.json")
        module.run(instructions)
    else:
        logger.error(f"Invalid premium module choice: {aaarg}")
