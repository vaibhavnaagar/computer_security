#!/usr/bin/python

import rpclib
import sys
import os
import sandboxlib
import urllib
import hashlib
import socket
import bank_client as bank
import zoodb

from debug import *

## Cache packages that the sandboxed code might want to import
import time
import errno

def get_token(username):
    #print("[get_token] UID: ", os.getresuid(), "GID: ", os.getresgid())
    if os.getresuid()[0] != 0:  # If not root
        return None
    db = zoodb.cred_setup()
    if not db:
        return None
    cred = db.query(zoodb.Cred).get(username)
    if cred:
        return cred.token
    else:
        return None

class ProfileAPIServer(rpclib.RpcServer):
    def __init__(self, user, visitor):
        uid = 61060
        gid = 60000     # To access person and transfer db
        self.user = user
        self.visitor = visitor
        self.token = get_token(user)
        os.setresgid(gid, gid, gid)
        os.setresuid(uid, uid, uid)

    def rpc_get_self(self):
        return self.user

    def rpc_get_visitor(self):
        return self.visitor

    def rpc_get_xfers(self, username):
        xfers = []
        for xfer in bank.get_log(username):
            #print("[get_xfers] UID: ", os.getresuid(), "GID: ", os.getresgid())
            xfers.append({ 'sender': xfer.sender,
                           'recipient': xfer.recipient,
                           'amount': xfer.amount,
                           'time': xfer.time,
                         })
        return xfers

    def rpc_get_user_info(self, username):
        person_db = zoodb.person_setup()
        p = person_db.query(zoodb.Person).get(username)
        #print("[get_user_info] UID: ", os.getresuid(), "GID: ", os.getresgid())

        if not p:
            return None
        return { 'username': p.username,
                 'profile': p.profile,
                 'zoobars': bank.balance(username),
               }

    def rpc_xfer(self, target, zoobars):
        #print("[rpc_xfer] UID: ", os.getresuid(), "GID: ", os.getresgid())
        bank.transfer(self.user, target, zoobars, self.token)

def run_profile(pcode, profile_api_client):
    globals = {'api': profile_api_client}
    exec pcode in globals

class ProfileServer(rpclib.RpcServer):
    def rpc_run(self, pcode, user, visitor):
        uid = 61050

        userdir = '/tmp/' + hashlib.sha256(user).hexdigest()
        if not os.path.isdir(userdir):
            os.mkdir(userdir)
            os.chmod(userdir, 0700)
            os.chown(userdir, uid, uid)

        (sa, sb) = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        pid = os.fork()
        if pid == 0:
            if os.fork() <= 0:
                sa.close()
                ProfileAPIServer(user, visitor).run_sock(sb)
                sys.exit(0)
            else:
                sys.exit(0)
        sb.close()
        os.waitpid(pid, 0)

        sandbox = sandboxlib.Sandbox(userdir, uid, '/profilesvc/lockfile')
        with rpclib.RpcClient(sa) as profile_api_client:
            return sandbox.run(lambda: run_profile(pcode, profile_api_client))

(_, dummy_zookld_fd, sockpath) = sys.argv

s = ProfileServer()
s.run_sockpath_fork(sockpath)
