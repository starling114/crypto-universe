from web3 import Web3

from core.models.token import Token
from core.models.chain import Chain
from utils import CONFIGS, ERC20_ABI, NULL_TOKEN_ADDRESS


def build_token(web3, chain=None, symbol=None, token_address=None):
    address = token_address if token_address is not None else chain.tokens[symbol]

    if address == "" or address == NULL_TOKEN_ADDRESS:
        return Token(symbol, NULL_TOKEN_ADDRESS, None, 18)
    else:
        address = web3.to_checksum_address(address)
        token_contract = web3.eth.contract(address=address, abi=ERC20_ABI)
        token_decimals = token_contract.functions.decimals().call()
        token_symbol = token_contract.functions.symbol().call()

        return Token(token_symbol, address, token_contract, token_decimals)


def build_chain(chain):
    config = CONFIGS["chains"][chain]

    return Chain(chain, config["chain_id"], config["native_token"], config["tokens"], config["scan"], config["rpcs"])


def build_web3(chain):
    return Web3(Web3.HTTPProvider(chain.random_rpc()))