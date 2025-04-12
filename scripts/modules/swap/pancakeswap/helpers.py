from utils import load_json

FACTORY_ABI = load_json("modules/swap/pancakeswap/factory_abi.json")
FACTORY_CONTRACT_ADDRESS = "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865"

ROUTER_ABI = load_json("modules/swap/pancakeswap/router_abi.json")
ROUTER_CONTRACT_ADDRESS = "0x13f4EA83D0bd40E75C8222255bc855a974568Dd4"

QUOTER_ABI = load_json("modules/swap/pancakeswap/quoter_abi.json")
QUOTER_CONTRACT_ADDRESS = "0xB048Bbc1Ee6b733FFfCFb9e9CeF7375518e25997"

V2_ROUTER_ABI = load_json("modules/swap/pancakeswap/v2_router_abi.json")
V2_ROUTER_CONTRACT_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
