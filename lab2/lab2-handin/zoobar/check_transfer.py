#!/usr/bin/python
import rpclib


with rpclib.client_connect('../banksvc/sock') as c:
        c.call('transfer', sender='gintoki', recipient='kagura', zoobars=10, token='abc')
