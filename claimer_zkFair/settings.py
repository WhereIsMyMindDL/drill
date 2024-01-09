

# ===================================== options ===================================== #

#------main-options------#
shuffle = False                                                     # True / False. если нужно перемешать кошельки

decimal_places = 7                                                  # количество знаков, после запятой для генерации случайных чисел

delay_wallets = [100, 200]                                          # минимальная и максимальная задержка между кошельками
delay_transactions = [20, 40]                                       # минимальная и максимальная задержка между транзакциями
waiting_gas = 40                                                    # макс значение газа при котором будет работать скрипт
RETRY_COUNT = 3                                                     # кол-во попыток при возникновении ошибок

bridge_with_orbiter = False                                          # True / False. если нужно отправить USDC в zkFair из optimism
value_bridge = 0.5                                                  # процент от баланса USDC 1-100%, 0.1-10%

withdraw_from_okex = False                                          # True / False. если нужно выводить с окекса


#------okex-options------#
symbolWithdraw = "USDC"                                             # символ токена, не менять, нахуя вам другой токен
network = "Optimism (Bridged)"                                      # ID сети, тоже, работает только в сети оптимизм
amount = [4, 4.5]                                                     # минимальная и максимальная сумма
transfer_subaccount = False                                         # перевод с субакков на мейн

class API:
    # okx API
    okx_apikey = ""
    okx_apisecret = ""
    okx_passphrase = ""

#------bot-options------#
bot_status = False                                                  # True / False
bot_token  = ''                                                     # telegram bot token
bot_id     = 0                                                      # telegram id

# =================================== end-options =================================== #