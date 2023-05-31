from web3 import Web3
from web3.auto import w3
import random
from tqdm import tqdm
import time
from loguru import logger
from sys import stderr
import telebot
import json
import requests
import fake_useragent
from bs4 import BeautifulSoup



#----main-options----#
delay_wallets = [20, 40]          # минимальная и максимальная задержка между кошельками
count_transactions = [3, 5]       # минимальное и максимальное количество транзакций для одного кошелька
#----end-main-options----#

#----second-options----#
rpc_bsc = 'https://rpc.ankr.com/bsc'                                # rpc BSC
rpc_polygon = 'https://polygon.llamarpc.com'                        # rpc Polygon
gas_price = 1                                                       # газ прайс в gwei
decimal_places = 4                                                  # количество знаков, после запятой для генерации случайных чисел
#----end-second-options----#

#----bot-options----#
TG_BOT_SEND = False                                                 # True / False. Если True, тогда будет отправлять результаты
TG_TOKEN    = ''                                                    # токен от тг-бота
TG_ID       = 0                                                     # id твоего телеграмма
#----end-bot-options----#


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

def sleeping(x):
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

list_send = []

def send_msg():
    try:
        str_send = '\n'.join(list_send)
        bot = telebot.TeleBot(TG_TOKEN)
        bot.send_message(TG_ID, str_send, parse_mode='html')
    except Exception as error:
        logger.error(error)

def add_gas_limit(transaction):

    try:
        gasLimit = rpc_url_bsc.eth.estimate_gas(transaction)
        transaction['gas'] = int(gasLimit * random.uniform(1.1, 1.3))
    except:
        transaction['gas'] = random.randint(2000000, 3000000)

    return transaction

def get_token_id(address):
    global tokenId
    try:
        headers = {
            "user-agent": fake_useragent.UserAgent().random
        }
        url = f"https://bscscan.com/token/generic-tokenholder-inventory?m=normal&contractAddress=0x40a2a882c82ad7cc74e5f58cde7612c07956d4a6&a={address}&pUrl=token"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        tokenid = soup.find_all("td")
        return int(str(tokenid)[66:72])
    except:
        logger.error(f'NFT not found')
        return None

def convert_to(number, base, upper=False):
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    if base > len(digits): return None
    result = ''
    while number > 0:
        result = digits[number % base] + result
        number //= base
    return result.upper() if upper else result

def approve_loyalty_program_nft(wallet):
    global tokenId
    try:
        private_key = wallet.split(':')[1]
        address = rpc_url_bsc.to_checksum_address(wallet.split(':')[0].lower())
        abi = json.loads('[{"inputs":[{"internalType":"uint256","name":"_mintStartTime","type":"uint256"},{"internalType":"uint256","name":"_mintEndTime","type":"uint256"},{"internalType":"uint256","name":"_mintLimit","type":"uint256"},{"internalType":"string","name":"_metadataUri","type":"string"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"ApprovalCallerNotOwnerNorApproved","type":"error"},{"inputs":[],"name":"ApprovalQueryForNonexistentToken","type":"error"},{"inputs":[],"name":"ApproveToCaller","type":"error"},{"inputs":[],"name":"BalanceQueryForZeroAddress","type":"error"},{"inputs":[],"name":"InvalidQueryRange","type":"error"},{"inputs":[],"name":"MintERC2309QuantityExceedsLimit","type":"error"},{"inputs":[],"name":"MintToZeroAddress","type":"error"},{"inputs":[],"name":"MintZeroQuantity","type":"error"},{"inputs":[],"name":"OwnerQueryForNonexistentToken","type":"error"},{"inputs":[],"name":"OwnershipNotInitializedForExtraData","type":"error"},{"inputs":[],"name":"TransferCallerNotOwnerNorApproved","type":"error"},{"inputs":[],"name":"TransferFromIncorrectOwner","type":"error"},{"inputs":[],"name":"TransferToNonERC721ReceiverImplementer","type":"error"},{"inputs":[],"name":"TransferToZeroAddress","type":"error"},{"inputs":[],"name":"URIQueryForNonexistentToken","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"fromTokenId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"toTokenId","type":"uint256"},{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"ConsecutiveTransfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"explicitOwnershipOf","outputs":[{"components":[{"internalType":"address","name":"addr","type":"address"},{"internalType":"uint64","name":"startTimestamp","type":"uint64"},{"internalType":"bool","name":"burned","type":"bool"},{"internalType":"uint24","name":"extraData","type":"uint24"}],"internalType":"struct IERC721A.TokenOwnership","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"tokenIds","type":"uint256[]"}],"name":"explicitOwnershipsOf","outputs":[{"components":[{"internalType":"address","name":"addr","type":"address"},{"internalType":"uint64","name":"startTimestamp","type":"uint64"},{"internalType":"bool","name":"burned","type":"bool"},{"internalType":"uint24","name":"extraData","type":"uint24"}],"internalType":"struct IERC721A.TokenOwnership[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"userAddress","type":"address"}],"name":"getMintSurplus","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"mintEndTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"mintLimit","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"mintStartTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_mintStartTime","type":"uint256"},{"internalType":"uint256","name":"_mintEndTime","type":"uint256"}],"name":"setMintTimes","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"tokensOfOwner","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"start","type":"uint256"},{"internalType":"uint256","name":"stop","type":"uint256"}],"name":"tokensOfOwnerIn","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
        address_contract = rpc_url_bsc.to_checksum_address("0x40a2A882c82AD7cC74E5f58Cde7612c07956D4A6")

        contract = rpc_url_bsc.eth.contract(address=address_contract, abi=abi)
        tokenId = get_token_id(address)

        build_tx_data = {
            'gasPrice': w3.to_wei(gas_price, 'gwei'),
            'from': rpc_url_bsc.to_checksum_address(address.lower()),
            'nonce': rpc_url_bsc.eth.get_transaction_count(address),
            'value': 0
        }

        transaction = contract.functions.approve("0xE09828f0DA805523878Be66EA2a70240d312001e", tokenId).build_transaction(build_tx_data)
        add_gas_limit(transaction)

        signed_txn = rpc_url_bsc.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url_bsc.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Approve check status tx - {rpc_url_bsc.to_hex(tx_hash)}')
        txstatus = rpc_url_bsc.eth.wait_for_transaction_receipt(tx_hash).status
        if txstatus == 1:
            logger.success(f'Approve Loyalty program NFT :  https://bscscan.com/tx/{rpc_url_bsc.to_hex(tx_hash)}')
        else:
            logger.error(f'Approve Loyalty program NFT :  https://bscscan.com/tx/{rpc_url_bsc.to_hex(tx_hash)}')
    except:
        logger.error(f'ERROR approve Loyalty program NFT - {address}')

def bridge_loyalty_program_nft(wallet, tokenId):
    try:
        private_key = wallet.split(':')[1]
        address = rpc_url_bsc.to_checksum_address(wallet.split(':')[0].lower())
        address_token = rpc_url_bsc.to_checksum_address("0x40a2A882c82AD7cC74E5f58Cde7612c07956D4A6")

        transaction = {
            'to': rpc_url_bsc.to_checksum_address('0xE09828f0DA805523878Be66EA2a70240d312001e'),
            'data': f'0xac7b22dc000000000000000000000000{address_token[2:]}00000000000000000000000000000000000000000000000000000000000{convert_to(tokenId, 16)}0000000000000000000000000000000000000000000000000000000000000004000000000000000000000000{address[2:]}',
            'chainId': 56,
            'gasPrice': w3.to_wei(gas_price, 'gwei'),
            'from': rpc_url_bsc.to_checksum_address(address.lower()),
            'nonce': rpc_url_bsc.eth.get_transaction_count(address),
            'value': int(rpc_url_bsc.to_wei(0.001, "ether"))
        }

        add_gas_limit(transaction)

        signed_txn = rpc_url_bsc.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url_bsc.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Bridge check status tx - {rpc_url_bsc.to_hex(tx_hash)}')
        txstatus = rpc_url_bsc.eth.wait_for_transaction_receipt(tx_hash).status
        if txstatus == 1:
            logger.success(f'Bridge Loyalty program NFT :  https://bscscan.com/tx/{rpc_url_bsc.to_hex(tx_hash)}')
            list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_SUCCESS}Polihedra Bridge NFT - transaction success')
            with open('success wallets.txt', 'a') as file:
                file.write(f'{address}:{private_key} PolihedraBridgeNFT-transactionSuccess\n')
        else:
            logger.error(f'Bridge Loyalty program NFT :  https://bscscan.com/tx/{rpc_url_bsc.to_hex(tx_hash)}')
            list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_ERROR}Polihedra Bridge NFT - transaction failed')
            with open('failed wallets.txt', 'a') as file:
                file.write(f'{address}:{private_key} PolihedraBridgeNFT-TransactionFailed\n')
    except:
        logger.error(f'ERROR bridge Loyalty program NFT - {address}')
        list_send.append(f'{number_wallets}/{count_wallets} : {address} \n \n{STR_ERROR}Polihedra Bridge NFT - transaction failed')
        with open('failed wallets.txt', 'a') as file:
            file.write(f'{address}:{private_key} PolihedraBridgeNFT-TransactionFailed\n')

if __name__ == '__main__':
    rpc_url_bsc = Web3(Web3.HTTPProvider(rpc_bsc))
    rpc_url_polygon = Web3(Web3.HTTPProvider(rpc_polygon))
    print(f'Subscribe: https://t.me/CryptoMindYep')
    print(f'Total wallets: {len(wallets)}\n')
    count_wallets = len(wallets)
    while wallets:
        list_send.clear()
        number_wallets += 1
        wallet = wallets.pop(0)
        print(f'{number_wallets}/{count_wallets}: {wallet.split(":")[0]}\n')
        tokenId = 0

        approve_loyalty_program_nft(wallet)
        time.sleep(8)
        bridge_loyalty_program_nft(wallet, tokenId)

        if TG_BOT_SEND == True:
            send_msg()
        sleeping(random.randint(delay_wallets[0], delay_wallets[1]))
        print()
print(input(f'Если помог скрипт: https://t.me/CryptoMindYep\nMetamask: 0x5AfFeb5fcD283816ab4e926F380F9D0CBBA04d0e'))