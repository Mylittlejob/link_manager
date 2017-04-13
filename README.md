# Link Manager for LinkedIn campaign

## Software used
SQLite, Python, uwsgi (htttp server). Has an importer to import the CSV file with links.

## Setup
  * clone the repository
  * cd <repository>
  * create a virtualenv (`virtualenv -p /usr/bin/python3.5 .venv`)
  * source the virtualenv (`source .venv/bin/activate`)
  * `pip install -r requirements.txt`
  * run uwsgi (`uwsgi --http :9090 --wsgi-file server.py`)
