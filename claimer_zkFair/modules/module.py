from loguru import logger
from pyuseragents import random as random_ua
from requests import Session
from datetime import datetime
from eth_account.messages import encode_defunct


from .myaccount import Account
from help import check_gas, retry, sign_and_send_transaction, sleeping_between_transactions, SUCCESS, FAILED, get_tx_data

send_list = ''
class module(Account):
    def __init__(self, id, private_key, proxy, rpc):
        super().__init__(id=id, private_key=private_key, proxy=proxy, rpc=rpc)

        self.session = Session()
        self.session.headers['user-agent'] = random_ua()
        self.proxy = proxy
        if self.proxy != None:
            self.session.proxies.update({'http': self.proxy, 'https': self.proxy})
        else:
            logger.warning('You are not using proxy')

    @check_gas
    @retry
    def check_elligble(self):
        global send_list
        current_date_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        text_origin = current_date_time + "GET/api/airdrop?address=" + self.address

        message = encode_defunct(text=text_origin)
        text_signature = self.w3.eth.account.sign_message(message, private_key=self.private_key)
        signature_value = text_signature.signature.hex()


        self.session.headers.update({
            'authority': 'airdrop.zkfair.io',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://zkfair.io',
            'referer': 'https://zkfair.io/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
        })

        response = self.session.get(f'https://airdrop.zkfair.io/api/airdrop?address={self.address}&API-SIGNATURE={signature_value}&TIMESTAMP={current_date_time}', headers=self.session.headers,).json()

        account_profit = response['data']['account_profit']
        logger.info(f'zkFair: account profit - {"{:0.2f}".format(int(account_profit) / 10**18)} ZKF')
        index = response['data']['index']

        if account_profit == 0:
            send_list += (f'\n{FAILED}zkFair: 0 ZKF')
            return True

        response = self.session.get(f'https://airdrop.zkfair.io/api/airdrop_merkle?address={self.address}&API-SIGNATURE={signature_value}&TIMESTAMP={current_date_time}', headers=self.session.headers,).json()

        data = "0xae0b51df" + self.w3.to_bytes(int(index)).hex().zfill(64) + self.w3.to_bytes(int(account_profit)).hex().zfill(64) + "00000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000014"
        print(f'{"{:0.2f}".format(int(account_profit) / 10**18)} ZKF')
        proof_array = [item.replace("0x", "") for item in response["data"]["proof"]]
        data = data + "".join(proof_array)
        # print(data)
        tx_data = get_tx_data(self, to='0x53c390b02339519991897b59eb6d9e0b211eb840', value=0, data=data)

        logger.info(f'zkFair: claim {"{:0.9f}".format(int(account_profit) / 10**18)} ZKF')
        txstatus, tx_hash = sign_and_send_transaction(self, tx_data)

        if txstatus == 1:
            logger.success(f'zkFair: claim {"{:0.9f}".format(int(account_profit) / 10**18)} ZKF : {self.scan + tx_hash}')
            send_list += (f'\n{SUCCESS}zkFair: claim {"{:0.4f}".format(int(account_profit) / 10**18)} ZKF - [tx hash]({self.scan + tx_hash})')

        else:
            logger.error(f'zkFair: claim {"{:0.9f}".format(int(account_profit) / 10**18)} ZKF : {self.scan + tx_hash}')
            send_list += (f'\n{FAILED}zkFair: claim {"{:0.4f}".format(int(account_profit) / 10**18)} ZKF - failed')


    def main(self):
        global send_list
        send_list = ''
        try:
            module.check_elligble(self)
            # sleeping_between_transactions()

            return send_list

        except Exception as e:
            logger.error(f'Failed: {str(e)}')
            return send_list