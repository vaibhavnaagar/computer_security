from zoodb import *
from debug import *
import auth_client as auth
import time

def transfer(sender, recipient, zoobars, token):
    if not auth.check_token(sender, token):
        print("Sender '%s' token didn't match " % sender)
        return
    if sender == recipient:
        print("Sender and recipient are same")
        return
    bankdb = bank_setup()
    senderp = bankdb.query(Bank).get(sender)
    recipientp = bankdb.query(Bank).get(recipient)

    if recipientp is None:
        print("No such recipient exist: %s" % recipient)
        return
        
    sender_balance = senderp.zoobars - zoobars
    recipient_balance = recipientp.zoobars + zoobars

    if sender_balance < 0 or recipient_balance < 0:
        raise ValueError()

    senderp.zoobars = sender_balance
    recipientp.zoobars = recipient_balance
    bankdb.commit()

    transfer = Transfer()
    transfer.sender = sender
    transfer.recipient = recipient
    transfer.amount = zoobars
    transfer.time = time.asctime()

    transferdb = transfer_setup()
    transferdb.add(transfer)
    transferdb.commit()

def balance(username):
    db = bank_setup()
    person = db.query(Bank).get(username)
    if person:
        return person.zoobars
    else:
        return 0

def register(username):
    db = bank_setup()
    if db.query(Bank).get(username):
        return True
    newbank = Bank()
    newbank.username = username
    db.add(newbank)
    db.commit()
    return False
