from loguru import logger
from pyuseragents import random as random_ua
from requests import Session
import time

from .myaccount import Account
from help import check_gas, retry, sign_and_send_transaction, SUCCESS, FAILED, get_tx_data

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

        current_date_time = time.time()
        current_date_time = str(current_date_time)[:14]
        current_date_time = int(current_date_time.replace('.', ''))


        self.session.headers.update({
            'authority': 'nft.scroll.io',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://scroll.io',
            'referer': 'https://scroll.io/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
        })
        params = {
            'timestamp': current_date_time,
        }
        response = self.session.get(f'https://nft.scroll.io/p/{self.address}.json', params=params, headers=self.session.headers).json()

        data = '0x186aaba2000000000000000000000000' + response['metadata']['deployer'][2:] + '000000000000000000000000' + response['metadata']['deployer'][2:] + '000000000000000000000000' + response['metadata']['firstDeployedContract'][2:] + '000000000000000000000000' + response['metadata']['firstDeployedContract'][2:] + '000000000000000000000000000000000000000000000000000' + response['metadata']['rarityData'][2:] + '00000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000015'
        proof_array = [item.replace("0x", "") for item in response["proof"]]
        data = data + "".join(proof_array)


        tx_data = get_tx_data(self, to='0x74670a3998d9d6622e32d0847ff5977c37e0ec91', value=0, data=data)

        logger.info(f'ScrollOrigins: claim NFT')
        txstatus, tx_hash = sign_and_send_transaction(self, tx_data)

        if txstatus == 1:
            logger.success(
                f'ScrollOrigins: claim NFT : {self.scan + tx_hash}')
            send_list += (
                f'\n{SUCCESS}ScrollOrigins: claim NFT - [tx hash]({self.scan + tx_hash})')

        else:
            logger.error(
                f'ScrollOrigins: claim NFT : {self.scan + tx_hash}')
            send_list += (f'\n{FAILED}ScrollOrigins: claim NFT - failed')

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