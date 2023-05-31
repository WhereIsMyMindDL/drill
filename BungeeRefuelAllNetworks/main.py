import json
from web3 import Web3
import random
from tqdm import tqdm
import time
from loguru import logger
from sys import stderr
import telebot


"""Перед запуском, рекомендую проверять комиссию на сайте"""

#----main-options----#
delay_wallets = [40, 70]                                            # минимальная и максимальная задержка между кошельками
from_network = 'Optimism'                                           # Arbitrum | zkEVM | zkSync | BSC | Optimism | Ethereum | Polygon | Avalanche
to_network = 'zkEVM'                                                # Arbitrum | zkEVM | zkSync | BSC | Optimism | Avalanche | Polygon
value = [0.0053, 0.0064]                                            # минимальное и максимальное кол-во нативных тугриков для бриджа
decimal_places = 6                                                  # количество знаков, после запятой для генерации случайных чисел
need_gas = [False, 30]                                              # True / False. Если True, будет ждать пока газ не опустится до введенного значения, только для сети эфира
TG_BOT_SEND = False                                                 # True / False. Если True, тогда будет отправлять результаты
TG_TOKEN = ''                                                       # токен тг-бота
TG_ID = 0                                                           # id твоего телеграмма
#----end-main-options----#



data = {
    'Arbitrum': ['https://endpoints.omniatech.io/v1/arbitrum/one/public', '0xc0e02aa55d10e38855e13b64a8e1387a04681a00', 42161, 'https://arbiscan.io/tx/', 'ETH'],
    'zkEVM': ['https://rpc.ankr.com/polygon_zkevm', '0x555a64968e4803e27669d64e349ef3d18fca0895', 1101, 'https://zkevm.polygonscan.com/tx/', 'ETH'],
    'zkSync': ['https://mainnet.era.zksync.io', '0x7Ee459D7fDe8b4a3C22b9c8C7aa52AbadDd9fFD5', 324, 'https://explorer.zksync.io/tx/', 'ETH'],
    'Ethereum': ['https://eth.llamarpc.com', '0xb584d4be1a5470ca1a8778e9b86c81e165204599', 1, 'https://etherscan.io/tx/', 'ETH'],
    'Optimism': ['https://endpoints.omniatech.io/v1/op/mainnet/public', '0x5800249621da520adfdca16da20d8a5fc0f814d8', 10, 'https://optimistic.etherscan.io/tx/', 'ETH'],
    'BSC': ['https://rpc.ankr.com/bsc', '0xbe51d38547992293c89cc589105784ab60b004a9', 56, 'https://bscscan.com/tx/', 'BNB'],
    'Polygon': ['https://polygon.llamarpc.com', '0xac313d7491910516e06fbfc2a0b5bb49bb072d91', 137, 'https://polygonscan.com/tx/', 'MATIC'],
    'Avalanche': ['https://avalanche-c-chain.publicnode.com', '0x040993fbf458b95871cd2d73ee2e09f4af6d56bb', 43114, 'https://snowtrace.io/tx/', 'AVAX']
}






logger.remove()
logger.add(stderr, format="<lm>{time:YYYY-MM-DD HH:mm:ss}</lm> | <level>{level: <8}</level>| <lw>{message}</lw>")

list_send = []
STR_SUCCESS = '✅ '
STR_ERROR = '❌ '

number_wallets = 0

with open('wallets.txt', 'r') as file:     # address:privatekey в файл wallets.txt
	wallets = [row.strip() for row in file]

with open('failed wallets.txt', 'w') as file:
    pass
with open('success wallets.txt', 'w') as file:
    pass

def wait_gas():
    gas = rpc_url.to_wei(need_gas[1], 'gwei')
    while True:
        gasPrice = int(rpc_url.eth.gas_price * random.uniform(1.09, 1.14))
        if gasPrice < gas:
            logger.info(f'actual gas {round(rpc_url.from_wei(gasPrice, "gwei"), 1)} Gwei Lets go')
            return gasPrice
        logger.info(f'wait {need_gas[1]} Gwei, actual {round(rpc_url.from_wei(gasPrice, "gwei"), 1)} Gwei')
        time.sleep(180)

def send_message():
    try:
        str_send = '\n'.join(list_send)
        bot = telebot.TeleBot(TG_TOKEN)
        bot.send_message(TG_ID, str_send, parse_mode='html')
    except Exception as error:
        logger.error(error)

def sleeping(x):
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

def add_gas_limit(transaction):

    try:
        gasLimit = rpc_url.eth.estimate_gas(transaction)
        transaction['gas'] = int(gasLimit * random.uniform(1.1, 1.3))
    except:
        transaction['gas'] = random.randint(200000, 700000)

    return transaction

def bridge(wallet, withdrawal):
    try:
        private_key = wallet.split(':')[1]
        address = rpc_url.to_checksum_address(wallet.split(':')[0].lower())
        abi = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"destinationReceiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"destinationChainId","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Donation","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"}],"name":"GrantSender","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"}],"name":"RevokeSender","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"srcChainTxHash","type":"bytes32"}],"name":"Send","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdrawal","type":"event"},{"inputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"isEnabled","type":"bool"}],"internalType":"struct GasMovr.ChainData[]","name":"_routes","type":"tuple[]"}],"name":"addRoutes","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable[]","name":"receivers","type":"address[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"},{"internalType":"bytes32[]","name":"srcChainTxHashes","type":"bytes32[]"},{"internalType":"uint256","name":"perUserGasAmount","type":"uint256"},{"internalType":"uint256","name":"maxLimit","type":"uint256"}],"name":"batchSendNativeToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"chainConfig","outputs":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"isEnabled","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"destinationChainId","type":"uint256"},{"internalType":"address","name":"_to","type":"address"}],"name":"depositNativeToken","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"chainId","type":"uint256"}],"name":"getChainData","outputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"isEnabled","type":"bool"}],"internalType":"struct GasMovr.ChainData","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"grantSenderRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"processedHashes","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"revokeSenderRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"receiver","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes32","name":"srcChainTxHash","type":"bytes32"},{"internalType":"uint256","name":"perUserGasAmount","type":"uint256"},{"internalType":"uint256","name":"maxLimit","type":"uint256"}],"name":"sendNativeToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"senders","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"_isEnabled","type":"bool"}],"name":"setIsEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"setPause","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"setUnPause","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"withdrawBalance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"}],"name":"withdrawFullBalance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]')
        contract = rpc_url.eth.contract(address=rpc_url.to_checksum_address(data[from_network][1]), abi=abi)

        build_tx_data = {
            'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.14)),
            'from': rpc_url.to_checksum_address(address.lower()),
            'nonce': rpc_url.eth.get_transaction_count(address),
            'value': int(rpc_url.to_wei(withdrawal, "ether")),
        }
        if from_network == 'BSC':
            build_tx_data['gasPrice'] = rpc_url.to_wei(1, 'gwei')

        if need_gas[0] and from_network == 'Ethereum':
            build_tx_data['gasPrice'] = wait_gas()

        transaction = contract.functions.depositNativeToken(data[to_network][2], address).build_transaction(build_tx_data)
        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Refuel {withdrawal} {data[from_network][4]} from {from_network} to {to_network} check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status

        if txstatus == 1:
            logger.success(f'Refuel {withdrawal} {data[from_network][4]} from {from_network} to {to_network} - {data[from_network][3]}{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_SUCCESS}Refuel - transaction success')
            with open('success wallets.txt', 'a') as file:
                file.write(f'{address}:{private_key}\n')

        else:
            logger.error(f'Refuel - {data[from_network][3]}{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_ERROR}Refuel - transaction failed')
            with open('failed wallets.txt', 'a') as file:
                file.write(f'{address}:{private_key} Refuel-TransactionFailed\n')
    except:
        logger.error(f'ERROR Refuel - {address}')
        list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_ERROR}Refuel - transaction failed')
        with open('failed wallets.txt', 'a') as file:
            file.write(f'{address}:{private_key} Refuel-TransactionFailed\n')

if __name__ == '__main__':
    rpc_url = Web3(Web3.HTTPProvider(data[from_network][0]))
    print(f'Subscribe: https://t.me/CryptoMindYep')
    print(f'Total wallets: {len(wallets)}\n')

    count_wallets = len(wallets)

    while wallets:

        list_send.clear()
        number_wallets += 1
        wallet = wallets.pop(0)
        print(f'{number_wallets}/{count_wallets} - {wallet.split(":")[0]}\n')

        withdrawal = round(random.uniform(value[0], value[1]), decimal_places)  # рандом кол-во токенов для бриджа

        bridge(wallet, withdrawal)

        if TG_BOT_SEND == True:
            send_message()
        sleeping(random.randint(delay_wallets[0], delay_wallets[1]))
        print()

print(input(f'Если помог скрипт: https://t.me/CryptoMindYep\nMetamask: 0x5AfFeb5fcD283816ab4e926F380F9D0CBBA04d0e'))