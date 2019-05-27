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

* [Docker](https://docker.com)
* [Python 2.7](http://www.python.org/)

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

Docker setup:
```bash
    # Create the production database and the initial Mailgun routes
    docker run \
        --interactive \
        --tty \
        --env DATABASE_URL="mysql://user:password@localhost/stratagem" \
        --env FLASK_ENV="production" \
        taeram/stratagem \
        bash -c "python ./app/database.py create && python manage.py mailgun setup"

    # Run the application
    docker run \
        --publish 8080:80 \
        --env API_KEY="foo" \
        --env DATABASE_URL="mysql://user:password@localhost/stratagem" \
        --env FLASK_ENV="production" \
        --env MAILGUN_API_KEY="foo" \
        taeram/stratagem
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
curl http://your-domain.com/whitelist/ -H "Authorization: secret_api_key"  -F "email=bill@example.com&destination=me@example.com"

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
