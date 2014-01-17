from app import app
from database import db
from flask import request
import re

def is_authenticated():
    if 'Authorization' not in request.headers:
        return False

    return app.config['API_KEY'] == request.headers['Authorization'].strip()

regex_address = re.compile("^(.+)@(.+)$", re.IGNORECASE|re.MULTILINE)
def parse_address(email_address):
    """ Parse an email address into local part and domain name"""
    r = regex_address.search(email_address.lower())
    if r and r.groups():
        local = r.group(1)
        domain = r.group(2)
    else:
        return None

    return [ local, domain ]
