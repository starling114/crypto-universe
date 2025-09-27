import asyncio
import importlib
import json
import os
import random
import re
import sys
import time
import traceback
from decimal import Decimal

import requests
from loguru import logger

NULL_TOKEN_ADDRESS = "0x0000000000000000000000000000000000000000"


def debug_mode():
    return os.getenv("DEBUG") == "true"


logger.remove()
logger.level("INFO", color="<bold><cyan>")
logger.level("WARNING", color="<bold><yellow>")
logger.level("DEBUG", color="<bold><blue>")
level = "DEBUG" if debug_mode() else "INFO"
format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}"
logger.add(sys.stdout, colorize=True, format=format, level=level)


class ExecutionError(Exception):
    pass


def load_json(file_path, check_existance=True):
    if not os.path.exists(file_path):
        if check_existance:
            raise FileNotFoundError(f"File not found: {file_path}")
        else:
            return {}

    with open(file_path, "r") as file:
        return json.load(file)


SECRETS = load_json("../backend/modules/crypto_universe/secrets.json", check_existance=False)
CONFIGS = load_json("../configs.json")
PRIVATE_CONFIGS = load_json("../private_configs.json", check_existance=False)
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


async def async_sleep(delay, max_delay=None):
    if max_delay is not None:
        delay = random.uniform(delay, max_delay)

    await asyncio.sleep(delay)


def import_premium_module(file, name):
    location = ".".join(file.split("-"))
    try:
        module = importlib.import_module(f"modules.premium.{location}")
    except ImportError:
        try:
            module = importlib.import_module(f"modules.premium.private.{location}")
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
        secrets = load_json(f"modules/{location}/secrets.json", check_existance=False)
        module.run(instructions, secrets)
    else:
        logger.error(f"Invalid premium module choice: {aaarg}")


def random_decimal(a: Decimal, b: Decimal) -> Decimal:
    lower = min(a, b)
    upper = max(a, b)
    scale = upper - lower
    return lower + Decimal(str(random.random())) * scale


def format_time_seconds(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def parse_number_text(text):
    formatted_text = text.replace("$", "").replace("%", "").replace(",", "").replace("x", "").strip()
    match = re.search(r"(-?\$?[\d,.]+)", formatted_text)
    if match:
        return Decimal(match.group(1))
    else:
        return None
