import json

INVOLVED_CHAINS = ['Ethereum']

RPC = {
    'Ethereum': 'https://rpc.ankr.com/eth',
    'Optimism': 'https://rpc.ankr.com/optimism',
    'zkfair': 'https://rpc.zkfair.io',
    'BSC': '',
    'Gnosis': '',
    'Polygon': '',
    'Fantom': '',
    'Arbitrum': 'https://rpc.ankr.com/arbitrum',
    'Avalanche': '',
    'zkSync': 'https://zksync-era.rpc.thirdweb.com',
    'zkEVM': 'https://rpc.ankr.com/polygon_zkevm',
    'Zora': '',
    'Scroll': 'https://1rpc.io/scroll',
    'nova': '',
    'Linea': 'https://1rpc.io/linea',
}

SCANS = {
    'Ethereum': 'https://etherscan.io/tx/',
    'Optimism': 'https://optimistic.etherscan.io/tx/',
    'BSC': 'https://bscscan.com/tx/',
    'Gnosis': 'https://gnosisscan.io/tx/',
    'Polygon': 'https://polygonscan.com/tx/',
    'Fantom': 'https://ftmscan.com/tx/',
    'Arbitrum': 'https://arbiscan.io/tx/',
    'Avalanche': 'https://snowtrace.io/tx/',
    'zkSync': 'https://explorer.zksync.io/tx/',
    'zkEVM': 'https://zkevm.polygonscan.com/tx/',
    'Zora': 'https://explorer.zora.energy/tx/',
    'Scroll': 'https://scrollscan.com/tx/',
    'Linea': 'https://lineascan.build/tx/',
    'zkfair': 'https://scan.zkfair.io/tx/',
}

CHAIN_IDS = {
    'Ethereum': 1,
    'Optimism': 10,
    'BSC': 56,
    'Gnosis': 100,
    'Polygon': 137,
    'Fantom': 250,
    'Arbitrum': 42161,
    'Avalanche': 43114,
    'zkSync': 324,
    'zkEVM': 1101,
    'Zora': 7777777,
    'Scroll': 534352,
    'Linea': 59144,
    'zkfair': 42766,
}

CHAIN_NAMES = {
    1: 'Ethereum',
    10: 'Optimism',
    56: 'BSC',
    100: 'Gnosis',
    137: 'Polygon',
    250: 'Fantom',
    42161: 'Arbitrum',
    43114: 'Avalanche',
    1313161554: 'Aurora',
    324: 'zkSync',
    1101: 'zkEVM',
    7777777: 'Zora',
    534352: 'Scroll',
    59144: 'Linea',
    42766: 'zkfair',
}

EIP1559_CHAINS = ['Ethereum', 'Zora', 'Optimism']

NATIVE_TOKEN_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

NATIVE_DECIMALS = 18