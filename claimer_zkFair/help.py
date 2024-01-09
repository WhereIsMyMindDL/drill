from loguru import logger
import time
from web3 import Web3
from tqdm import trange
from colorama import Fore
from sys import stderr
import telebot
import random
from statistics import mean

from vars import EIP1559_CHAINS
from settings import RETRY_COUNT, delay_wallets, delay_transactions, waiting_gas


send_list = []
logger.remove()
logger.add(stderr, format="<lm>{time:YYYY-MM-DD HH:mm:ss}</lm> | <level>{level: <8}</level>| <lw>{message}</lw>")

number_wallets = 0
SUCCESS = '✅ '
FAILED = '⚠️ '
ERROR = '❌ '


def retry(func):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries <= RETRY_COUNT:
            try:
                time.sleep(15)
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error | {e}")
                time.sleep(10)
                retries += 1

    return wrapper

def sleeping_between_wallets():
    x = random.randint(delay_wallets[0], delay_wallets[1])
    for i in trange(x, desc=f'{Fore.LIGHTBLACK_EX}sleep...', ncols=50, bar_format='{desc}  {n_fmt}/{total_fmt}s |{bar}| {percentage:3.0f}%'):
        time.sleep(1)
    print()

def sleeping_between_transactions():
    x = random.randint(delay_transactions[0], delay_transactions[1])
    for i in trange(x, desc=f'{Fore.LIGHTBLACK_EX}sleep between transaction...', ncols=65, bar_format='{desc}  {n_fmt}/{total_fmt}s |{bar}| {percentage:3.0f}%'):
        time.sleep(1)
    print()

@retry
def send_message(bot_token, bot_id, send_list):
    try:
        str_send = [i for i in send_list if i is not None]
        str_send_without_none = '\n'.join(str_send)
        bot = telebot.TeleBot(bot_token)
        bot.send_message(bot_id, str_send_without_none, parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as error:
        logger.error(error)

def check_gas(func):
    def wrapper(*args, **kwargs):
        wait_gas()
        return func(*args, **kwargs)
    return wrapper

@retry
def wait_gas():
    try:
        rpc_url_eth = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
        gas = rpc_url_eth.to_wei(waiting_gas, 'gwei')
        while True:
            gasPrice = int(rpc_url_eth.eth.gas_price)
            if gasPrice < gas:
                break
            logger.info(f'Waiting {waiting_gas} Gwei. Actual: {round(rpc_url_eth.from_wei(gasPrice, "gwei"), 1)} Gwei')
            time.sleep(120)
    except:
        wait_gas()

def convert_to(number, base, upper=False):
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    if base > len(digits): return None
    result = ''
    while number > 0:
        result = digits[number % base] + result
        number //= base
    return result.upper() if upper else result

def intro(wallets):
    print()
    print(f'Subscribe: https://t.me/CryptoMindYep')
    print(f'Total wallets: {len(wallets)}\n')
    #input('Press ENTER: ')

    print()
    print(f'| {Fore.LIGHTGREEN_EX}claimer zkFair{Fore.RESET} |'.center(100, '='))
    print('\n')

def outro():
    for i in trange(3, desc=f'{Fore.LIGHTBLACK_EX}End process...', ncols=50, bar_format='{desc} {percentage:3.0f}%'):
        time.sleep(1)
    print(f'{Fore.RESET}\n')
    print(f'| {Fore.LIGHTGREEN_EX}END{Fore.RESET} |'.center(100, '='))
    print()
    print(input(f'Если помог скрипт: https://t.me/CryptoMindYep\nMetamask: 0x5AfFeb5fcD283816ab4e926F380F9D0CBBA04d0e'))

def add_gas_limit(transaction, rpc_url):
    try:
        gasLimit = rpc_url.eth.estimate_gas(transaction)
        transaction['gas'] = int(gasLimit * random.uniform(1.1, 1.2))
    except:
        transaction['gas'] = random.randint(380000, 420000)
    return transaction

def get_tx_data_withABI(self, value=0):
    if self.rpc in EIP1559_CHAINS:
        maxPriorityFeePerGas = self.w3.eth.max_priority_fee
        fee_history = self.w3.eth.fee_history(10, 'latest', [10, 90])
        baseFee = round(mean(fee_history['baseFeePerGas']))
        maxFeePerGas = maxPriorityFeePerGas + round(baseFee * 1.1)

        tx_data = {
            "from": self.address,
            "maxFeePerGas": maxFeePerGas,
            "maxPriorityFeePerGas": maxPriorityFeePerGas,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "value": value,
        }
        
    else:
        tx_data = {
            "from": self.address,
            "gasPrice": int(self.w3.eth.gas_price * 1.05),
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "value": value,
        }

    return tx_data

def get_tx_data(self, to, value=0, data=None):
    tx_data = {
        "chainId": self.w3.eth.chain_id,
        "from": self.address,
        "to": self.w3.to_checksum_address(to),
        "gasPrice": int(self.w3.eth.gas_price * 1.05),
        "nonce": self.w3.eth.get_transaction_count(self.address),
        "value": value,
        "gas": 0,
    }
    if data != None:
        tx_data["data"] = data

    return tx_data

def sign_and_send_transaction(self, transaction, gas=None):
    if gas == None:
        gas = int(self.w3.eth.estimate_gas(transaction) * 1.2)

    transaction.update({"gas": gas})

    signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)

    tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    time.sleep(12)

    txstatus = self.w3.eth.wait_for_transaction_receipt(tx_hash).status

    tx_hash = self.w3.to_hex(tx_hash)

    return txstatus, tx_hash
