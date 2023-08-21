from web3 import Web3
import random
from tqdm import tqdm
import time
from loguru import logger
from sys import stderr
import telebot
from tqdm import trange
from colorama import Fore

#----main-options----#
delay_wallets = [60, 80]                                            # минимальная и максимальная задержка между кошельками
delay_transactions = [20, 30]                                       # минимальная и максимальная задержка между транзакциями
gas = [300000, 310000]                                              # минимальный и максимальный GasLimit
gasPrice = 0.005                                                    # gasPrice в Gwei
count_nft = 1                                                       # кол-во нфт для из data которые нужно минтить, если все то можно указать любое число
rpc = 'https://zora.rpc.thirdweb.com'                               # rpc ноды
mint_everyday = True                                                # True / False. если нужно минтить каждый день
shuffle = True                                                      # True / False. если нужно перемешать кошельки
use_proxies = True                                                  # True / False. Если True, тогда будет использовать прокси (прокси = приватники)
TG_BOT_SEND = True                                                  # True / False. Если True, тогда будет отправлять результаты
TG_TOKEN    = ''                                                    # токен тг-бота
TG_ID       = 0                                                     # id твоего телеграмма
#----end-main-options----#


# кол-во нфт менять в data удалением или добавлением новых нфт с +- похожим hex из сканера в формате 'название':['адрес контракта', 'hex'], (минт говна рандомится)

data = {
    'Zora Cola Classic': ['0xFa177a7eDC2518E70F8f8Ee159fA355D6b727257', '0xa0712d6800000000000000000000000000000000000000000000000000000000000000030021fb3f'],
    'A Great Day': ['0x4de73D198598C3B4942E95657a12cBc399E4aDB5', '0xa0712d6800000000000000000000000000000000000000000000000000000000000000010021fb3f'],
    'Dithered Zorb': ['0x48D913ee06B66599789F056A0e48Bb45Caf3b4e9', '0xa0712d6800000000000000000000000000000000000000000000000000000000000000030021fb3f'],
    'GoldenFla': ['0x4073a52A3fc328D489534Ab908347eC1FcB18f7f', '0xa0712d6800000000000000000000000000000000000000000000000000000000000000030021fb3f'],
    'ZoraEyeNFT': ['0x8A43793D26b5DBd5133b78A85b0DEF8fB8Fce9B3', '0xa0712d6800000000000000000000000000000000000000000000000000000000000000630021fb3f'],
    'ZoraOGPass': ['0x266b7E8Df0368Dd4006bE5469DD4EE13EA53d3a4', '0xa0712d6800000000000000000000000000000000000000000000000000000000000000030021fb3f'],
    'Allure': ['0x53cb0B849491590CaB2cc44AF8c20e68e21fc36D', '0xa0712d6800000000000000000000000000000000000000000000000000000000000000030021fb3f'],
}






logger.remove()
logger.add(stderr, format="<lm>{time:YYYY-MM-DD HH:mm:ss}</lm> | <level>{level: <8}</level>| <lw>{message}</lw>")

list_send = []
STR_SUCCESS = '✅ '
STR_ERROR = '❌ '

number_wallets = 0


with open('wallets.txt', 'r') as file:     # privatekey в файл wallets.txt
	wallets = [row.strip() for row in file]

with open('proxies.txt', 'r') as file:     # login:password@ip:port в файл proxy.txt
	proxies = [row.strip() for row in file]

def sleeping_wallets(x):
    for i in trange(x, desc=f'{Fore.LIGHTBLACK_EX}sleep...', ncols=50, bar_format='{desc}  {n_fmt}/{total_fmt}s |{bar}| {percentage:3.0f}%'):
        time.sleep(1)

def sleeping_transactions(x):
    for i in trange(x, desc=f'{Fore.LIGHTBLACK_EX}sleep between transaction...', ncols=65, bar_format='{desc}  {n_fmt}/{total_fmt}s |{bar}| {percentage:3.0f}%'):
        time.sleep(1)
    print()

def intro():
    print()
    print(f'Subscribe: https://t.me/CryptoMindYep')
    print(f'Total wallets: {len(wallets)}\n')
    print(f'| {Fore.LIGHTGREEN_EX}!fundrop mint in zora{Fore.RESET} |'.center(100, '='))
    print('\n')

def outro():
    for i in trange(3, desc=f'{Fore.LIGHTBLACK_EX}End process...', ncols=50, bar_format='{desc} {percentage:3.0f}%'):
        time.sleep(1)
    print(f'{Fore.RESET}\n')
    print(f'| {Fore.LIGHTGREEN_EX}END{Fore.RESET} |'.center(100, '='))
    print()
    print(input(f'Если помог скрипт: https://t.me/CryptoMindYep\nMetamask: 0x5AfFeb5fcD283816ab4e926F380F9D0CBBA04d0e'))

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

def sleeping_one_day(x):
    for i in trange(x, desc=f'{Fore.LIGHTBLACK_EX}sleep for 24 hours...', ncols=75, bar_format='{desc}  {n_fmt}/{total_fmt}s |{bar}| {percentage:3.0f}%'):
        time.sleep(1)

def zora_mint(address, private_key, key, rpc_url):
    try:
        transaction = {
            'to': rpc_url.to_checksum_address(data[key][0]),
            'value': 0,
            'data': data[key][1],
            'chainId': 7777777,
            'nonce': rpc_url.eth.get_transaction_count(address),
            'gasPrice': int(rpc_url.to_wei(gasPrice, 'gwei')),
            'gas': int(random.randint(gas[0], gas[1]))
        }

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Mint {key} NFT check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status

        if txstatus == 1:
            logger.success(f'Mint {key} NFT - https://explorer.zora.energy/tx/{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'\n{STR_SUCCESS}Mint {key} NFT - transaction success')

        else:
            logger.error(f'Mint NFT private key - {private_key} - https://explorer.zora.energy/tx/{rpc_url.to_hex(tx_hash)}')
            list_send.append(f'\n{STR_ERROR}Mint {key} NFT - transaction failed')
    except:
        logger.error(f'ERROR Mint NFT private key - {private_key}')
        list_send.append(f'\n{STR_ERROR}Mint {key} NFT - transaction failed')

def check_rpc(rpc_url, retry = 1):
    if rpc_url.is_connected() == True:
        return rpc_url.is_connected()
    else:
        logger.error(f'error connect to rpc... sleep 10 sec')
        time.sleep(10)
        if retry == 2:
            logger.error(f'failed')
            return rpc_url.is_connected()
        check_rpc(rpc_url, retry+1)

if __name__ == '__main__':
    intro()

    count_wallets = len(wallets)
    wallets_list = []
    proxy_list = []
    for i in wallets:
        wallets_list.append(i)
    for i in proxies:
        proxy_list.append(i)
    def start():
        global number_wallets

        if shuffle:
            random.shuffle(wallets_list)

        for private_key in wallets_list:
            list_send.clear()
            if use_proxies == True:
                try:
                    proxy = proxy_list[number_wallets]
                    rpc_url = Web3(Web3.HTTPProvider(rpc, request_kwargs={"proxies": {'https': "http://" + proxy, 'http': "http://" + proxy}}))
                except:
                    rpc_url = Web3(Web3.HTTPProvider(rpc))
            else:
                rpc_url = Web3(Web3.HTTPProvider(rpc))

            number_wallets += 1
            account = rpc_url.eth.account.from_key(private_key)
            address = account.address
            print(f'{number_wallets}/{count_wallets} - {address}\n')
            list_send.append(f'{number_wallets}/{count_wallets} : {address}')

            if check_rpc(rpc_url) != True:
                if use_proxies == True:
                    logger.error(f'{proxy} proxy not working')
                    list_send.append(f'\n{STR_ERROR}rpc not working...')

            keys = list(data.keys())
            random.shuffle(keys)

            k = 0
            for key in keys:
                if count_nft == k:
                    break
                zora_mint(address, private_key, key, rpc_url)
                k += 1
                if count_nft != k:
                    sleeping_transactions(random.randint(delay_transactions[0], delay_transactions[1]))


            if TG_BOT_SEND == True:
                if number_wallets == count_wallets:
                    list_send.append(f'\nSubscribe: https://t.me/CryptoMindYep')
                send_message()
            if number_wallets != count_wallets:
                sleeping_wallets(random.randint(delay_wallets[0], delay_wallets[1]))
            if mint_everyday and number_wallets == count_wallets:
                sleeping_one_day(86400)
                print()
                number_wallets = 0
                start()
            print()
    start()
outro()