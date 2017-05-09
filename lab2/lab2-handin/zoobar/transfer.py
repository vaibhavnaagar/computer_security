from flask import g, render_template, request

from login import requirelogin
from zoodb import *
from debug import *
import bank_client as bank
import traceback

@catch_err
@requirelogin
def transfer():
    warning = None
    try:
        if 'recipient' in request.form:
            try:
                zoobars = int(request.form['zoobars'])
            except:
                zoobars = 0
            bank.transfer(g.user.person.username,
                          request.form['recipient'], zoobars, g.user.token)
            warning = "Sent %d zoobars" % zoobars
    except (KeyError, ValueError, AttributeError) as e:
        traceback.print_exc()
        warning = "Transfer to %s failed" % request.form['recipient']

    return render_template('transfer.html', warning=warning)
