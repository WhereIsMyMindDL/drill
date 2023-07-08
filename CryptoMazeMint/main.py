from web3 import Web3
import random
from tqdm import tqdm
import time
from loguru import logger
from sys import stderr
import telebot


#----main-options----#
delay_wallets = [100, 150]                                          # минимальная и максимальная задержка между кошельками
numberNFT = 2                                                       # номер нфт 1-5
rpc = 'https://1rpc.io/zksync2-era'                                 # rpc ноды
TG_BOT_SEND = False                                                 # True / False. Если True, тогда будет отправлять результаты
TG_TOKEN    = ''                                                    # токен тг-бота
TG_ID       = 0                                                     # id твоего телеграмма
#----end-main-options----#


addressNFT = '0x3F9931144300f5Feada137d7cfE74FAaa7eF6497'           # адресс контракта

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
        transaction['gas'] = random.randint(1100000, 1300000)

    return transaction

def maze_mint(wallet):
    try:
        private_key = wallet.split(':')[1]
        address = rpc_url.to_checksum_address(wallet.split(':')[0].lower())

        data = {
            1: f'0x57bc3d78000000000000000000000000{address[2:]}00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
            2: f'0x57bc3d78000000000000000000000000{address[2:]}00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
            3: f'0x57bc3d78000000000000000000000000{address[2:]}00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
            4: f'0x57bc3d78000000000000000000000000{address[2:]}00000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
            5: f'0x57bc3d78000000000000000000000000{address[2:]}00000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
        }

        transaction = {
            'to': rpc_url.to_checksum_address(addressNFT),
            'value': 0,
            'data': data[numberNFT],
            'chainId': 324,
            'nonce': rpc_url.eth.get_transaction_count(address),
            'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.14)),
        }

        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Mint CryptoMaze NFT #{numberNFT} check status tx - {rpc_url.to_hex(tx_hash)}')
        time.sleep(60)
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status

        if txstatus == 1:
            logger.success(f'Mint CryptoMaze NFT #{numberNFT} - https://explorer.zksync.io/tx/{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_SUCCESS}CryptoMaze NFT - transaction success')
            with open('success wallets.txt', 'a') as file:
                file.write(f'{address}\n')

        else:
            logger.error(f'Mint CryptoMaze NFT #{numberNFT} - https://explorer.zksync.io/tx/{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_ERROR}CryptoMaze NFT - transaction failed')
            with open('failed wallets.txt', 'a') as file:
                file.write(f'{address}:{private_key}\n')

    except:
        logger.error(f'{address} - ERROR MInt CryptoMaze NFT #{numberNFT}')
        list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_ERROR}CryptoMaze NFT - transaction failed')
        with open('failed wallets.txt', 'a') as file:
            file.write(f'{address}:{private_key}\n')

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

        maze_mint(wallet)

        if TG_BOT_SEND == True:
            send_message()
        if number_wallets != count_wallets:
            sleeping(random.randint(delay_wallets[0], delay_wallets[1]))
        print()

print(input(f'Если помог скрипт: https://t.me/CryptoMindYep\nMetamask: 0x5AfFeb5fcD283816ab4e926F380F9D0CBBA04d0e'))