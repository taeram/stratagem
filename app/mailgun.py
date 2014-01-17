from app import app
from flask import url_for
from flask.ext.script import Manager, prompt
from database import db, \
                     Domain
import requests

manager = Manager(usage="Manage Mailgun setup")

@manager.command
def setup():
    """Setup a new domain in Mailgun"""
    stratagem_domain_name = prompt("What is the domain name you where Stratagem is hosted? [https://example.herokuapp.com]")

    domain_name = prompt("What is a domain name you want to use with Stratagem? [example.com]")

    # Lookup the domain name
    domain = db.session.query(Domain).\
                       filter(Domain.name == domain_name).\
                       first()

    # Add the domain name if it doesn't exist
    if domain is None:
        domain = Domain(name=domain_name)
        db.session.add(domain)
        db.session.commit()

    email_destination = prompt("Where should we forward whitelisted emails? [joe@example.com]")

    # Add the route to Mailgun for this domain name
    url = "%s/routes" % app.config['MAILGUN_API_URL']
    auth = ('api', app.config['MAILGUN_API_KEY'])
    params = {
        "priority": 50,
        "expression": 'match_recipient(".*\.[a-z0-9]{%s}@%s")' % (app.config['LOCAL_PART_HASH_LENGTH'], domain.name),
        "action": [
            'forward("%s/email/")' % stratagem_domain_name,
            'forward("%s")' % email_destination,
            'stop()'
        ]
    }

    r = requests.post(url, params=params, auth=auth)
    if r.status_code > 200:
        raise Exception(r.text)
    else:
        print r.text

def mailgun_explicit_whitelist(email_address, email_destination):
    # Add the route to Mailgun for this email address
    url = "%s/routes" % app.config['MAILGUN_API_URL']
    auth = ('api', app.config['MAILGUN_API_KEY'])
    params = {
        "priority": 49,
        "expression": 'match_recipient("%s")' % (email_address),
        "action": [
            'forward("%s")' % url_for("message_collection", _external=True),
            'forward("%s")' % email_destination,
            'stop()'
        ]
    }

    r = requests.post(url, params=params, auth=auth)
    if r.status_code > 200:
        return False

    return True
