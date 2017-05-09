#!/usr/bin/python
#
# Insert bank server code here.
#

import rpclib
import sys
import bank
from debug import *

class BankRpcServer(rpclib.RpcServer):
    ## Fill in RPC methods here.
    def rpc_transfer(self, sender, recipient, zoobars, token):
        bank.transfer(sender, recipient, zoobars, token)

    def rpc_balance(self, username):
        return bank.balance(username)

    def rpc_register(self, username):
        return bank.register(username)

(_, dummy_zookld_fd, sockpath) = sys.argv

s = BankRpcServer()
s.run_sockpath_fork(sockpath)
