import sys
from modules import *
from utils import log_error

MODULES = {"1": WithdrawOkx, "2": BridgeRelay, "3": Transfer}
ARGS_MODULES = {
    "withdraw-okx": WithdrawOkx,
    "bridge-relay": BridgeRelay,
    "transfer": Transfer,
}


def get_module(module):
    func = MODULES.get(module)
    if func:
        return func
    else:
        raise ValueError(f"Unsupported module: {module}")


def extract_from_args():
    aaarg = sys.argv[1]

    return ARGS_MODULES.get(aaarg, None)


def display_menu():
    print("Select a module to run:")
    print("1. Withdraw OKX")
    print("2. Bridge Relay")
    print("3. Transfer")

    choice = input("Enter your choice: ")

    return MODULES.get(choice, None)


if __name__ == "__main__":
    try:
        selected_module = None

        if len(sys.argv) > 1:
            selected_module = extract_from_args()
        else:
            selected_module = display_menu()

        if selected_module:
            selected_module.run()
        else:
            print("Invalid choice.")
    except Exception as e:
        log_error(e)
        # raise e
