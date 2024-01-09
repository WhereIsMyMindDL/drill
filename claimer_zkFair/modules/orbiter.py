from loguru import logger
import time
import json

from modules.myaccount import Account
from help import sign_and_send_transaction, sleeping_between_transactions, SUCCESS, FAILED, check_gas, retry, get_tx_data_withABI
from settings import value_bridge

chains = {
    "Optimism": ["0x7f5c764cbc14f9669b88837ca1490cca17c31607", "9007"],
    "zkSync": ["0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8", "9014"],
    "Scroll": ["0xe4edb277e41dc89ab076a1f049f4a3efa700bce8", "9019"],
    "zkfair": ["", "9019"],
}

with open('data/ABIORBITER.json') as file:
    ABIORBITER = json.load(file)

send_list = ''
class OrbiterBridge(Account):
    def __init__(self, id, private_key, proxy, rpc):
        super().__init__(id=id, private_key=private_key, proxy=proxy, rpc=rpc)
        self.contract = self.get_contract(contract_address=self.w3.to_checksum_address("0x7F5c764cBc14f9669B88837ca1490cCa17c31607"), abi=ABIORBITER)

    @check_gas
    @retry
    def bridge(self, from_chain, to_chain):
        global send_list
        balance = self.get_balance('0x7f5c764cbc14f9669b88837ca1490cca17c31607')
        value = (balance["balance_wei"] * value_bridge - 10000) // 10000 * 10000 + 9038

        tx_data = get_tx_data_withABI(self)
        transaction = self.contract.functions.transfer(self.w3.to_checksum_address('0x41d3D33156aE7c62c094AAe2995003aE63f587B3'), value).build_transaction(tx_data)
        logger.info(f'Orbiter: Bridge {"{:0.2f}".format(balance["balance"])} USDC from {from_chain} to {to_chain}')

        txstatus, tx_hash = sign_and_send_transaction(self, transaction)
        if txstatus == 1:
            logger.success(f'Orbiter: Bridge {"{:0.2f}".format(balance["balance"])} USDC {from_chain} to {to_chain}: {self.scan + tx_hash}')
            send_list += (f'\n{SUCCESS}Orbiter: Bridge {from_chain} to {to_chain} - [tx hash]({self.scan + tx_hash})')
            time.sleep(50)

        else:
            logger.error(f'Orbiter: Bridge {"{:0.2f}".format(balance["balance"])} USDC {from_chain} to {to_chain}: {self.scan + tx_hash}')
            send_list += (f'\n{FAILED}Orbiter: Bridge {from_chain} to {to_chain} - failed')

    def main(self, from_chain, to_chain):
        global send_list
        send_list = ''
        OrbiterBridge.bridge(self, from_chain, to_chain)
        sleeping_between_transactions()
        return send_list