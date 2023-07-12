from web3 import Web3
import random
from tqdm import tqdm
import time
from loguru import logger
from sys import stderr
import telebot
import json



#----main-options----#
delay_wallets = [60, 120]                                           # минимальная и максимальная задержка между кошельками
rpc_url = 'https://rpc.ankr.com/bsc'                                # rpc BSC
value = 0.002781377207839                                           # актуальное value для комиссии л0 из сканера
gas_price = 1                                                       # газ прайс в gwei
try_again = 1                                                       # кол-во попыток в случае возникновения ошибок
TG_BOT_SEND = False                                                 # True / False. Если True, тогда будет отправлять результаты
TG_TOKEN    = ''                                                    # токен от тг-бота
TG_ID       = 0                                                     # id твоего телеграмма
#----end-main-options----#



logger.remove()
logger.add(stderr, format="<lm>{time:YYYY-MM-DD HH:mm:ss}</lm> | <level>{level: <8}</level>| <lw>{message}</lw>")

with open('wallets.txt', 'r') as file:
	wallets = [row.strip() for row in file]

with open('failed wallets.txt', 'w') as file:
    pass
with open('success wallets.txt', 'w') as file:
    pass

number_wallets = 0

STR_SUCCESS = '✅ '
STR_ERROR = '❌ '
list_send = []

def sleeping(x):
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

def send_msg():
    try:
        str_send = '\n'.join(list_send)
        bot = telebot.TeleBot(TG_TOKEN)
        bot.send_message(TG_ID, str_send, parse_mode='html')
    except Exception as error:
        logger.error(error)

def add_gas_limit(transaction):

    try:
        gasLimit = rpc_url.eth.estimate_gas(transaction)
        transaction['gas'] = int(gasLimit * random.uniform(1.1, 1.3))
    except:
        transaction['gas'] = random.randint(400000, 500000)

    return transaction

def claim_nft(private_key, retry=0):
    global tokenId
    try:
        account = rpc_url.eth.account.from_key(private_key)
        address = account.address

        transaction = {
            'to': rpc_url.to_checksum_address('0x87a218ae43c136b3148a45ea1a282517794002c8'),
            'chainId': 56,
            'data': f'0x1249c58b',
            'gasPrice': rpc_url.to_wei(gas_price, 'gwei'),
            'from': rpc_url.to_checksum_address(address.lower()),
            'nonce': rpc_url.eth.get_transaction_count(address),
            'value': 0
        }

        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Claim NFT check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status
        if txstatus == 1:
            result = rpc_url.eth.get_transaction_receipt(rpc_url.to_hex(tx_hash))
            data = json.loads(rpc_url.to_json(result))
            tokenId = data['logs'][0]['topics'][3][-4:]
            logger.success(f'Claim Pandra NFT :  https://bscscan.com/tx/{rpc_url.to_hex(tx_hash)}')
        else:
            logger.error(f'Claim Pandra NFT :  https://bscscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            if retry < try_again:
                logger.info(f"try again in {10} sec.")
                sleeping(10)
                claim_nft(private_key, retry + 1)
    except:
        logger.error(f'ERROR claim Pandra NFT - {address}')
        if retry < try_again:
            logger.info(f"try again in {10} sec.")
            sleeping(10)
            claim_nft(private_key, retry + 1)

def approve_nft(private_key, retry=0):
    global tokenId
    try:
        account = rpc_url.eth.account.from_key(private_key)
        address = account.address

        transaction = {
            'to': rpc_url.to_checksum_address('0x87a218ae43c136b3148a45ea1a282517794002c8'),
            'data': f'0x095ea7b30000000000000000000000003668c325501322ceb5a624e95b9e16a019cdebe8000000000000000000000000000000000000000000000000000000000000{tokenId}',
            'gasPrice': rpc_url.to_wei(gas_price, 'gwei'),
            'chainId': 56,
            'nonce': rpc_url.eth.get_transaction_count(address),
            'value': 0,
        }

        add_gas_limit(transaction)
        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Approve check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status
        if txstatus == 1:
            logger.success(f'Approve Pandra NFT :  https://bscscan.com/tx/{rpc_url.to_hex(tx_hash)}')
        else:
            logger.error(f'Approve Pandra NFT :  https://bscscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            if retry < try_again:
                logger.info(f"try again in {10} sec.")
                sleeping(10)
                approve_nft(private_key, retry + 1)
    except:
        logger.error(f'ERROR approve Pandra NFT - {address}')
        if retry < try_again:
            logger.info(f"try again in {10} sec.")
            sleeping(10)
            approve_nft(private_key, retry + 1)

def bridge_nft(private_key, tokenId, retry=0):
    try:
        account = rpc_url.eth.account.from_key(private_key)
        address = account.address

        transaction = {
            'to': rpc_url.to_checksum_address('0x3668c325501322ceb5a624e95b9e16a019cdebe8'),
            'data': f'0xcfc9327400000000000000000000000087a218ae43c136b3148a45ea1a282517794002c8000000000000000000000000000000000000000000000000000000000000{tokenId}0000000000000000000000000000000000000000000000000000000000000099000000000000000000000000{address[2:]}00000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000022000100000000000000000000000000000000000000000000000000000000001b7740000000000000000000000000000000000000000000000000000000000000',
            'chainId': 56,
            'gasPrice': rpc_url.to_wei(gas_price, 'gwei'),
            'nonce': rpc_url.eth.get_transaction_count(address),
            'value': int(rpc_url.to_wei(value, "ether")),
        }

        add_gas_limit(transaction)
        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Bridge check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status
        if txstatus == 1:
            logger.success(f'Bridge Pandra NFT :  https://bscscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'\n{STR_SUCCESS}Polihedra Bridge Pandra NFT - transaction success')
            with open('success wallets.txt', 'a') as file:
                file.write(f'{address}\n')
        else:
            logger.error(f'Bridge Pandra NFT :  https://bscscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            if retry < try_again:
                logger.info(f"try again in {10} sec.")
                sleeping(10)
                bridge_nft(private_key, tokenId, retry + 1)
            else:
                list_send.append(f'\n{STR_ERROR} {retry} Polihedra Bridge Pandra NFT - transaction failed')
                with open('failed wallets.txt', 'a') as file:
                    file.write(f'{address}\n')
    except:
        logger.error(f'ERROR bridge Pandra NFT - {address}')
        if retry < try_again:
            logger.info(f"try again in {10} sec.")
            sleeping(10)
            bridge_nft(private_key, tokenId, retry + 1)
        else:
            list_send.append(f'\n{STR_ERROR} {retry} Polihedra Bridge Pandra NFT - transaction failed')
            with open('failed wallets.txt', 'a') as file:
                file.write(f'{address}\n')

if __name__ == '__main__':
    rpc_url = Web3(Web3.HTTPProvider(rpc_url))
    print(f'Subscribe: https://t.me/CryptoMindYep')
    print(f'Total wallets: {len(wallets)}\n')
    count_wallets = len(wallets)
    while wallets:
        list_send.clear()
        number_wallets += 1
        private_key = wallets.pop(0)
        account = rpc_url.eth.account.from_key(private_key)
        address = account.address
        print(f'{number_wallets}/{count_wallets}: {address}\n')

        list_send.append(f'{number_wallets}/{count_wallets} : {address}')
        tokenId = ''

        claim_nft(private_key)
        time.sleep(random.randint(7, 10))
        approve_nft(private_key)
        time.sleep(random.randint(7, 10))
        bridge_nft(private_key, tokenId)


        if TG_BOT_SEND == True:
            send_msg()
        if number_wallets != count_wallets:
            sleeping(random.randint(delay_wallets[0], delay_wallets[1]))
        print()
print(input(f'Если помог скрипт: https://t.me/CryptoMindYep\nMetamask: 0x5AfFeb5fcD283816ab4e926F380F9D0CBBA04d0e'))
