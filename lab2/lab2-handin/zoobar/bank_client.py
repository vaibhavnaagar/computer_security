from debug import *
from zoodb import *
import rpclib

@catch_err
def transfer(sender, recipient, zoobars, token):
    ## Fill in code here.
    with rpclib.client_connect('/banksvc/sock') as c:
        c.call('transfer', sender=sender, recipient=recipient, zoobars=zoobars, token=token)

@catch_err
def balance(username):
    ## Fill in code here.
    with rpclib.client_connect('/banksvc/sock') as c:
        return c.call('balance', username=username)

@catch_err
def get_log(username):
    ## Fill in code here.
    with rpclib.client_connect('/banksvc/sock') as c:
        return c.call('get_log', username=username)

@catch_err
def register(username):
    ## Fill in code here.
    with rpclib.client_connect('/banksvc/sock') as c:
        return c.call('register', username=username)

# This mehtod doesn't use bankdb, hence no need to put inside bank-server.py
# It can be called with ids of dynamic_svc
def get_log(username):
    db = transfer_setup()
    return db.query(Transfer).filter(or_(Transfer.sender==username,
                                         Transfer.recipient==username))
