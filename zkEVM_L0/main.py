from web3 import Web3
import random
from tqdm import tqdm
import time
from loguru import logger
from sys import stderr
import telebot
import json



#----main-options----#
delay_wallets = [200, 450]                                          # минимальная и максимальная задержка между кошельками
value = 0.001                                                       # actual value in ETH (найти актуальное можно в транзакциях по контракту во вкладке велью метод Cross Chain	 )
rpc = 'https://rpc.ankr.com/polygon_zkevm'                          # rpc ноды
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

def mint(wallet):
    try:
        global tokenId
        private_key = wallet.split(':')[1]
        address = rpc_url.to_checksum_address(wallet.split(':')[0].lower())
        addressNFT = '0x5a3b2e7f335be432f834b3f1bfef19b44d1f310c'  # адресс контракта
        transaction = {
            'to': rpc_url.to_checksum_address(addressNFT),
            'value': 0,
            'data': f'0x1249c58b',
            'chainId': 1101,
            'nonce': rpc_url.eth.get_transaction_count(address),
            'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.12)),
        }

        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Mint NFT check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status

        if txstatus == 1:
            result = rpc_url.eth.get_transaction_receipt(rpc_url.to_hex(tx_hash))
            data = json.loads(rpc_url.to_json(result))
            tokenId = data['logs'][0]['topics'][3][-5:]
            logger.success(f'Mint NFT - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')

        else:
            logger.error(f'Mint NFT - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')

    except:
        logger.error(f'Mint NFT - {address}')

def bridge(wallet, tokenId):
    try:
        private_key = wallet.split(':')[1]
        address = rpc_url.to_checksum_address(wallet.split(':')[0].lower())
        address_contract = '0x5a3b2e7f335be432f834b3f1bfef19b44d1f310c'  # адресс контракта

        transaction = {
            'to': rpc_url.to_checksum_address(address_contract),
            'value': int(rpc_url.to_wei(value, 'ether')),
            'data': f'0x1e128296000000000000000000000000000000000000000000000000000000000000006d00000000000000000000000000000000000000000000000000000000000{tokenId}',
            'chainId': 1101,
            'nonce': rpc_url.eth.get_transaction_count(address),
            'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.12)),
            'gas': 0,
        }

        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Bridge NFT check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status

        if txstatus == 1:

            logger.success(f'Bridge NFT - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_SUCCESS}Bridge NFT - transaction success')
            with open('success wallets.txt', 'a') as file:
                file.write(f'{address}\n')


        else:
            logger.error(f'Bridge NFT - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_ERROR}Bridge NFT - transaction failed')
            with open('failed wallets.txt', 'a') as file:
                file.write(f'{address}:{private_key} Bridge NFT-TransactionFailed\n')
    except:
        logger.error(f'{address} - ERROR Bridge NFT')
        list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_ERROR}Bridge NFT - transaction failed')
        with open('failed wallets.txt', 'a') as file:
            file.write(f'{address}:{private_key} Bridge NFT-TransactionFailed\n')


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
        tokenId = ''

        mint(wallet)
        time.sleep(7)
        bridge(wallet, tokenId)

        if TG_BOT_SEND == True:
            send_message()
        if number_wallets != count_wallets:
            sleeping(random.randint(delay_wallets[0], delay_wallets[1]))
        print()

print(input(f'Если помог скрипт: https://t.me/CryptoMindYep\nMetamask: 0x5AfFeb5fcD283816ab4e926F380F9D0CBBA04d0e'))