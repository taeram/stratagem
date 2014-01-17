Stratagem
=========

Stratagem allows easy management of catch-all email domains using [Mailgun](http://mailgun.com).

First, Stratagem will create a route in Mailgun for each catch-all domain. This route allows
any email to pass iff it matches a specific format. By default, the format is
`<local>.<8 digit hash>@<domain>`, e.g. `bob.abcd1234@example.com`.

By using a specific format for the email addresses along with Mailgun routes, we can
discard most of the incoming SPAM as it doesn't match the format.

Secondly, Stratagem provides monitoring for each email address, storing the total
number of received emails, and the average spam score for each address. This gives
a quick snapshot of the relative health of each email address, allowing you to
blacklist email addresses if they go bad.

Lastly, if you have existing email addresess which cannot be converted to the Stratagem
format, you can easily create Mailgun routes to whitelist them using Stratagem.

Requirements
============
You'll need the following:

* A [Heroku](https://www.heroku.com/) account, if you want to deploy to Heroku.
* A [Mailgun](http://mailgun.com) account
* [Python 2.7.3](http://www.python.org/)
* [pip](https://github.com/pypa/pip)
* [Virtualenv](https://github.com/pypa/virtualenv)

Mailgun Setup
=============

You'll need add your catch-all domain(s) to Mailgun, and update your MX records
so that all mail to each domain goes through Mailgun.

Setup
=====

Local development setup:
```bash
    # Clone the repo
    git clone git@github.com:taeram/stratagem.git
    cd ./stratagem

    # Setup and activate virtualenv
    virtualenv .venv
    source ./.venv/bin/activate

    # Install the pip requirements
    pip install -r requirements.txt

    # Create the initial Mailgun routes
    #   - This step should be run once per catch-all domain name
    python manage.py mailgun setup

    # Create the development database (SQLite by default)
    python manage.py database create

    # Start the application, prefixing with the required environment variables
    API_KEY="secret_api_key" MAILGUN_API_KEY="key-abcd1234" python server.py
```

Heroku setup:
```bash
    # Clone the repo
    git clone git@github.com:taeram/stratagem.git
    cd ./stratagem

    # Create your Heroku app, and add a database addon
    heroku apps:create
    heroku addons:add heroku-postgresql

    # Promote your postgres database (your URL name may differ)
    heroku pg:promote HEROKU_POSTGRESQL_RED_URL

    # Set an "API key" for authorization
    heroku config:set API_KEY="secret_api_key"

    # Get your API Key from your Mailgun account
    heroku config:set MAILGUN_API_KEY="key-abcd1234"

    # Set the flask environment
    heroku config:set FLASK_ENV=production

    # Push to Heroku
    git push heroku master

    # Create the production database
    heroku run python manage.py database create

    # Create the initial Mailgun routes
    #   - This step should be run once per catch-all domain name
    heroku run python manage.py mailgun setup
```

Usage
=====

To view a page of nicely formatted statistics for your domains,
visit `http://your-domain.com/list/<secret_api_key>`.

To list statistics for all email addresses:
```bash
curl http://your-domain.com/address/ -H "Authorization: secret_api_key"

# Response
[
    {
        "id": 3,
        "local": "steve.d73jc9s3",
        "domain": "example.com",
        "created": "2014-01-15 12:33:52",
        "avg_spam_score": 0.7,
        "date_last_received": "2014-01-17 04:41:12",
        "total_received": 12
    },
    {
        "id": 5,
        "local": "paul.c93kjdds",
        "domain": "example.com",
        "created": "2014-01-13 09:45:32",
        "avg_spam_score": 0.5,
        "date_last_received": "2014-01-15 03:11:52",
        "total_received": 43
    }
]
```

To get an individual email address:
```bash
curl http://your-domain.com/address/3 -H "Authorization: secret_api_key"

# Response
{
    "id": 3,
    "local": "steve.d73jc9s3",
    "domain": "example.com",
    "created": "2014-01-15 12:33:52",
    "avg_spam_score": 0.7,
    "date_last_received": "2014-01-13 04:41:12",
    "total_received": 12
}
```

To remove stats for an email address:
```bash
curl -X DELETE http://your-domain.com/address/3 -H "Authorization: secret_api_key"

# Response
{
    "id": 3,
    "local": "steve.d73jc9s3",
    "domain": "example.com",
    "avg_spam_score": 0.7,
    "date_last_received": "2014-01-13 04:41:12",
    "total_received": 12
}
```

If you have existing email addresses you don't want to convert to the new format,
you can whitelist a specific email address by:
```bash
curl http://your-domain.com/address/ -H "Authorization: secret_api_key"  -F "email=bill@example.com&destination=me@example.com"

# Response
{
    "status": "ok"
}
```

To list all domain names:
```bash
curl http://your-domain.com/domain/ -H "Authorization: secret_api_key"

# Response
[
    {
        "id": 3,
        "name": "example.com"
    },
    {
        "id": 4,
        "name": "example2.com"
    }
]
```

To get an individual domain name:
```bash
curl http://your-domain.com/domain/3 -H "Authorization: secret_api_key"

# Response
{
    "id": 3,
    "name": "example.com"
}
```

To delete a domain name and all stats for emails using that domain name:
```bash
curl -X DELETE http://your-domain.com/domain/3 -H "Authorization: secret_api_key"

# Response
{
    "id": 3,
    "name": "example.com"
}
```
