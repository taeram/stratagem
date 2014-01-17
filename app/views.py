from app import app
import os
from flask import render_template, \
                  request, \
                  send_from_directory
from helpers import is_authenticated, \
                    parse_address
from database import db, \
                     Address, \
                     Domain
from mailgun import mailgun_explicit_whitelist
import json
from datetime import datetime

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.png', mimetype='image/png')

@app.route('/', methods=['GET'])
def hello():
    return render_template('hello.html')

@app.route('/whitelist/', methods=['POST'])
def whitelist_collection():
    if not is_authenticated():
        return app.response_class(response='{"error": "Invalid API key"}', mimetype='application/json', status=403)

    if not mailgun_explicit_whitelist(request.form['email'], request.form['destination']):
        return app.response_class(response='{"error": "Could not whitelist email"}', mimetype='application/json', status=500)

    return app.response_class(response='{"status": "ok"}', mimetype='application/json')

@app.route('/domain/', methods=['GET'])
def domain_collection():
    if not is_authenticated():
        return app.response_class(response='{"error": "Invalid API key"}', mimetype='application/json', status=403)

    domains = db.session.query(Domain).\
                         all()
    response = []
    for domain in domains:
        response.append(domain.toObject())

    return app.response_class(response=json.dumps(response), mimetype='application/json')

@app.route('/domain/<int:domain_id>', methods=['GET', 'DELETE'])
def domain_item(domain_id):
    if not is_authenticated():
        return app.response_class(response='{"error": "Invalid API key"}', mimetype='application/json', status=403)

    row = db.session.query(Domain).\
                     filter(Domain.id == domain_id).\
                     first()

    if not row:
        return app.response_class(response='{"error": "Not found"}', mimetype='application/json', status=404)

    response = row.toObject()

    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()

    return app.response_class(response=json.dumps(response), mimetype='application/json')

@app.route('/address/', methods=['GET'])
def address_collection():
    if not is_authenticated():
        return app.response_class(response='{"error": "Invalid API key"}', mimetype='application/json', status=403)

    addresses = db.session.query(Address).\
                           all()
    response = []
    for address in addresses:
        response.append(address.toObject())

    return app.response_class(response=json.dumps(response), mimetype='application/json')

@app.route('/address/<int:address_id>', methods=['GET', 'DELETE'])
def address_item(address_id):
    if not is_authenticated():
        return app.response_class(response='{"error": "Invalid API key"}' % request.headers['Authorization'], mimetype='application/json', status=403)

    row = db.session.query(Address).\
                     filter(Address.id == address_id).\
                     first()

    if not row:
        return app.response_class(response='{"error": "Not found"}', mimetype='application/json', status=404)

    response = row.toObject()

    if request.method == 'DELETE':
        db.session.delete(row)
        db.session.commit()

    return app.response_class(response=json.dumps(response), mimetype='application/json')

@app.route('/email/', methods=['POST'])
def message_collection():
    # Extract the local_part@domain_name
    local_part, domain_name = parse_address(request.form.get('recipient'))

    # Get the domain name
    try:
        domain = db.session.query(Domain).\
                           filter(Domain.name == domain_name).\
                           first()
    except ValueError, e:
        return app.response_class(response='{"error": "%s"}' % e, mimetype='application/json', status=400)

    # Create the domain name if it doesn't exist
    if domain is None:
        domain = Domain(name=domain_name)
        db.session.add(domain)
        db.session.commit()

    # Get the address
    try:
        address = db.session.query(Address).\
                             filter(Address.local == local_part).\
                             filter(Address.domain_id == domain.id).\
                             first()
    except ValueError, e:
        return app.response_class(response='{"error": "%s"}' % e, mimetype='application/json', status=400)

    # Add the address if it doesn't exist
    if address is None:
        address = Address(local=local_part, domain_id=domain.id)
        db.session.add(address)
        db.session.commit()

    # Set the last received date
    address.date_last_received = datetime.utcnow()

    # Add one to the total number of received emails
    address.total_received += 1

    # Add the current spam score to the total
    address.total_spam_score += float(request.form.get('X-Mailgun-Sscore'))

    db.session.add(address)
    db.session.commit()

    return app.response_class(response='{"status": "ok"}', mimetype='application/json')

@app.route('/list/<api_key>', methods=['GET'])
def spam_list(api_key):
    if app.config['API_KEY'] != api_key:
        abort(403)

    addresses = db.session.query(Address).\
                order_by(db.desc(Address.created)).\
                all()

    return render_template('list.html', addresses=addresses, api_key=api_key)
