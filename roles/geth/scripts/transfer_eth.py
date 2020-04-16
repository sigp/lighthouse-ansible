#!/bin/python3

from web3 import Web3, IPCProvider
import sys
from web3.middleware import geth_poa_middleware

ipc_endpoint = sys.argv[1]
from_addr = Web3.toChecksumAddress(sys.argv[2])
to_addr = Web3.toChecksumAddress(sys.argv[3])
eth_amount = sys.argv[4]

web3 = Web3(IPCProvider(ipc_endpoint))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

web3.eth.sendTransaction({
    'from': from_addr,
    'to': to_addr,
    'value': web3.toWei(eth_amount, 'ether')
})
