from web3 import Web3
import random
from tqdm import tqdm
import time
from loguru import logger
from sys import stderr
import telebot



#----main-options----#
delay_wallets = [100, 150]                                          # минимальная и максимальная задержка между кошельками
addressNFT = '0x9d90669665607f08005cae4a7098143f554c59ef'           # адресс контракта нфт
value = 0.000777                                                    # Value из сканера
count_NFT = 1                                                       # кол-во нфт для минта
need_gas = [True, 30]                                               # True / False. Если True, будет ждать пока газ не опустится до введенного значения
rpc = 'https://eth.llamarpc.com'                                    # rpc ноды
TG_BOT_SEND = False                                                 # True / False. Если True, тогда будет отправлять результаты
TG_TOKEN    = ''                                                    # токен тг-бота
TG_ID       = 0                                                     # id твоего телеграмма
#----end-main-options----#



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
            return gasPrice
        logger.info(f'wait {need_gas[1]} Gwei, actual {round(rpc_url.from_wei(gasPrice, "gwei"), 1)} Gwei')
        time.sleep(120)

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

def zora_mint(wallet):
    try:
        private_key = wallet.split(':')[1]
        address = rpc_url.to_checksum_address(wallet.split(':')[0].lower())

        transaction = {
            'to': rpc_url.to_checksum_address(addressNFT),
            'value': int(rpc_url.to_wei(value, "ether")),
            'data': f'0xefef39a1000000000000000000000000000000000000000000000000000000000000000{count_NFT}',
            'chainId': 1,
            'nonce': rpc_url.eth.get_transaction_count(address),
            'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.14)),
        }
        if need_gas[0]:
            transaction['gasPrice'] = wait_gas()

        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'ZoraMint NFT check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status

        if txstatus == 1:
            logger.success(f'ZoraMint NFT (gasPrice {round(rpc_url.from_wei(transaction["gasPrice"], "gwei"), 1)} Gwei) - https://etherscan.io/tx/{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_SUCCESS}ZoraMint NFT - transaction success')
            with open('success wallets.txt', 'a') as file:
                file.write(f'{address}:{private_key} ZoraMint NFT-transactionSuccess\n')

        else:
            logger.error(f'ZoraMint NFT - https://etherscan.io/tx/{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_ERROR}ZoraMint NFT - transaction failed')
            with open('failed wallets.txt', 'a') as file:
                file.write(f'{address}:{private_key} ZoraMint NFT-TransactionFailed\n')

    except:
        logger.error(f'{address} - ERROR ZoraMint NFT')
        list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_ERROR}ZoraMint NFT - transaction failed')
        with open('failed wallets.txt', 'a') as file:
            file.write(f'{address}:{private_key} ZoraMint NFT-TransactionFailed\n')

if __name__ == '__main__':
    rpc_url = Web3(Web3.HTTPProvider(rpc))
    print(f'Subscribe: https://t.me/CryptoMindYep')
    print(f'Total wallets: {len(wallets)}\n')

    count_wallets = len(wallets)

    while wallets:

        list_send.clear()
        number_wallets += 1
        wallet = wallets.pop(0)
        print(f'{number_wallets}/{count_wallets} - {wallet.split(":")[0]}\n')

        zora_mint(wallet)

        if TG_BOT_SEND == True:
            send_message()
        sleeping(random.randint(delay_wallets[0], delay_wallets[1]))
        print()

print(input(f'Если помог скрипт: https://t.me/CryptoMindYep\nMetamask: 0x5AfFeb5fcD283816ab4e926F380F9D0CBBA04d0e'))
