import time
from sys import stderr
import random
import ccxt
from loguru import logger

from modules.myaccount import Account
from help import check_gas, retry, sign_and_send_transaction, sleeping_between_transactions, SUCCESS, FAILED, get_tx_data
from settings import stay_eth, amount, symbolWithdraw, network, decimal_places, transfer_subaccount, API

#----main-options----#
switch_cex = "okx"       # okx
proxy_server = ""

#----second-options----#
delay = [3, 5]             # минимальная и максимальная задержка
shuffle_wallets = "no"       # нужно ли мешать кошельки yes/no
#----end-all-options----#



logger.remove()
logger.add(stderr, format="<lm>{time:YYYY-MM-DD HH:mm:ss}</lm> | <level>{level: <8}</level>| <lw>{message}</lw>")



proxies = {
  "http": proxy_server,
  "https": proxy_server,
}

class Okex(Account):
    def __init__(self, id, private_key, proxy, rpc):
        super().__init__(id=id, private_key=private_key, proxy=proxy, rpc=rpc)

    @check_gas
    @retry
    def deposit_to_okex(self, addressokx):
        stay_eth_in_network = round(random.uniform(stay_eth[0], stay_eth[1]), decimal_places)
        value_in_eth = self.get_balance()["balance"] - stay_eth_in_network
        value_in_wei = int(self.w3.to_wei(value_in_eth, "ether"))

        transaction = get_tx_data(self, self.w3.to_checksum_address(addressokx), value=value_in_wei)

        logger.info(f'OKx: Deposit {"{:0.9f}".format(value_in_eth)} ETH from {self.rpc}...')
        txstatus, tx_hash = sign_and_send_transaction(self, transaction)

        if txstatus == 1:
            logger.success(f'OKx: Deposit {"{:0.9f}".format(value_in_eth)} ETH from {self.rpc} : {self.scan + tx_hash}')
            return (f'\n{SUCCESS}OKx: Deposit {"{:0.4f}".format(value_in_eth)} ETH from {self.rpc} - [tx hash]({self.scan + tx_hash})')
        else:
            logger.error(f'OKx: Deposit {"{:0.9f}".format(value_in_eth)} ETH from {self.rpc} : {self.scan + tx_hash}')
            return (f'\n{FAILED}OKx: Deposit {"{:0.4f}".format(value_in_eth)} ETH from {self.rpc} - failed')

    def withdraw_from_okex(self):

        if transfer_subaccount:
            Okex.transfer_from_subaccount(self)
            print()

        amount_to_withdrawal = round(random.uniform(amount[0], amount[1]), decimal_places)
        choose_cex(self.address, amount_to_withdrawal, 1)
        time.sleep(random.randint(delay[0], delay[1]))
        self.wait_balance(int(self.w3.to_wei(amount_to_withdrawal, 'ether') * 0.8), rpc=self.rpc, contract_address='0x7f5c764cbc14f9669b88837ca1490cca17c31607')
        sleeping_between_transactions()
        return (f'\n{SUCCESS}OKx: Withdraw {"{:0.4f}".format(amount_to_withdrawal)} ETH')


    def transfer_from_subaccount(self):
        exchange = ccxt.okx({
            'apiKey': API.okx_apikey,
            'secret': API.okx_apisecret,
            'password': API.okx_passphrase,
            'enableRateLimit': True,
            'proxies': proxies,
        })

        list_sub = exchange.private_get_users_subaccount_list()
        for sub_data in list_sub['data']:
            name_sub = sub_data['subAcct']
            balance = exchange.private_get_asset_subaccount_balances({'subAcct': name_sub, 'ccy': symbolWithdraw})
            sub_balance = balance['data'][0]['bal']
            logger.info(f'OKx: {name_sub} balance : {sub_balance} {symbolWithdraw}')
            if float(sub_balance) > 0:
                transfer = exchange.private_post_asset_transfer({"ccy": symbolWithdraw, "amt": str(sub_balance), "from": '6', "to": '6', "type": "2", "subAcct": name_sub})
                logger.success(f'OKx: transfer to main {sub_balance} {symbolWithdraw}')
            else:
                continue
        time.sleep(15)
        return True

def okx_withdraw(address, amount_to_withdrawal, wallet_number):
    exchange = ccxt.okx({
        'apiKey': API.okx_apikey,
        'secret': API.okx_apisecret,
        'password': API.okx_passphrase,
        'enableRateLimit': True,
        'proxies': proxies,
    })

    try:
        chainName = symbolWithdraw + "-" + network
        fee = get_withdrawal_fee(symbolWithdraw, chainName)
        exchange.withdraw(symbolWithdraw, amount_to_withdrawal, address,
            params={
                "toAddress": address,
                "chainName": chainName,
                "dest": 4,
                "fee": fee,
                "pwd": '-',
                "amt": amount_to_withdrawal,
                "network": network
            }
        )
        logger.success(f'OKx: Вывел {amount_to_withdrawal} {symbolWithdraw}')
        return amount_to_withdrawal
    except Exception as error:
        logger.error(f'OKx: Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error}')

def choose_cex(address, amount_to_withdrawal, wallet_number):
    if switch_cex == "okx":
        okx_withdraw(address, amount_to_withdrawal, wallet_number)

def get_withdrawal_fee(symbolWithdraw, chainName):
    exchange = ccxt.okx({
        'apiKey': API.okx_apikey,
        'secret': API.okx_apisecret,
        'password': API.okx_passphrase,
        'enableRateLimit': True,
        'proxies': proxies,
    })
    currencies = exchange.fetch_currencies()
    for currency in currencies:
        if currency == symbolWithdraw:
            currency_info = currencies[currency]
            network_info = currency_info.get('networks', None)
            if network_info:
                for network in network_info:
                    network_data = network_info[network]
                    network_id = network_data['id']
                    if network_id == chainName:
                        withdrawal_fee = currency_info['networks'][network]['fee']
                        if withdrawal_fee == 0:
                            return 0
                        else:
                            return withdrawal_fee
    raise ValueError(f"не могу получить сумму комиссии, проверьте значения symbolWithdraw и network")





