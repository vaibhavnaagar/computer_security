from zoodb import *
from debug import *

import hashlib
import random
import os, pbkdf2
import bank_client as bank

def newtoken(db, cred):
    hashinput = "%s%.10f" % (cred.password, random.random())
    cred.token = hashlib.md5(hashinput).hexdigest()
    db.commit()
    return cred.token

def login(username, password):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if not cred:
        return None
    if cred.password == pbkdf2.PBKDF2(password, cred.salt).hexread(32):
        return newtoken(db, cred)
    else:
        return None

def register(username, password):
    cred_db = cred_setup()
    person_db = person_setup()
    if person_db.query(Person).get(username) or cred_db.query(Cred).get(username) or bank.register(username):
        return None
    newperson = Person()
    newperson.username = username
    person_db.add(newperson)
    person_db.commit()

    newcred = Cred()
    newcred.username = username
    newcred.salt = os.urandom(8).encode('hex')
    newcred.password = pbkdf2.PBKDF2(password, newcred.salt).hexread(32)
    cred_db.add(newcred)
    cred_db.commit()
    return newtoken(cred_db, newcred)

def check_token(username, token):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if cred and cred.token == token:
        return True
    else:
        return False
