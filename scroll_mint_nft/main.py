from loguru import logger
import random

from help import send_message, sleeping_between_wallets, intro, outro, send_list
from settings import bot_status, bot_id, bot_token, shuffle
from modules.myaccount import Account
from modules.module import module


#------orbiter-options------#
from_chain = 'Scroll'                                             # не менять
to_chain = 'Scroll'                                               # не менять

def main():

    with open('proxies.txt', 'r') as file:  # login:password@ip:port в файл proxy.txt
        proxies = [row.strip() for row in file]
    with open('wallets.txt', 'r') as file:
        wallets = [row.strip() for row in file]

    intro(wallets)
    count_wallets = len(wallets)

    if len(proxies) == 0:
        proxies = [None] * len(wallets)
    if len(proxies) != len(wallets):
        logger.error('Proxies count doesn\'t match wallets count. Add proxies or leave proxies file empty')
        return

    data = [(wallets[i], proxies[i]) for i in range(len(wallets))]

    if shuffle:
        random.shuffle(data)

    for idx, (wallet, proxy) in enumerate(data, start=1):
        private_key = wallet



        account = Account(idx, private_key, proxy, from_chain)

        print(f'{idx}/{count_wallets} : {account.address}\n')
        send_list.append(f'{account.id}/{count_wallets} : [{account.address}]({"https://debank.com/profile/" + account.address})')

        try:

            send_list.append(module(account.id, account.private_key, account.proxy, 'Scroll').main())

        except Exception as e:
            logger.error(f'{idx}/{count_wallets} Failed: {str(e)}')

        if bot_status == True:
            if account.id == count_wallets:
                send_list.append(f'\nSubscribe: https://t.me/CryptoMindYep')

            send_message(bot_token, bot_id, send_list)
        send_list.clear()

        if idx != count_wallets:
            sleeping_between_wallets()
            print()


    outro()
main()