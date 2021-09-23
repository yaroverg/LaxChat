# Lax - a Slack clone ![ci badge](https://github.com/yaroverg/LaxChat/actions/workflows/github-ci.yml/badge.svg)


## Requirements

The user should have Python 3.8+, MySQL 5.7+ (or MariaDB 10.3+), Flask, and Flask-SocketIO installed, as well as the packages in `requirements.txt`.

### Secrets file
The app reads information from a `secrets.cfg` file, which should be located in the project root directory.
The user should create their own file which specifies a `PEPPER`, `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST` and a `SECRET_KEY`.
The pepper is used for password encryption while the username and password are used to establish a connection to the MySQL database. The secrey key is used for the flask app.
For example, the contents of the file would look like the following
```
[secrets]
PEPPER = abcd1234
DB_USERNAME = user123
DB_PASSWORD = password123
DB_HOST = 127.0.0.1
SECRET_KEY = xyz987
```


## Setup
Before using the app, the database needs to be set up with respect to the MySQL user provided in the secrets file.
First, a user needs to be created with a username and a password.
The user needs to be given privileges to two databases:
```
grant all privileges on lax_db.* to someUser@someHost;
grant all privileges on lax_test_db.* to someUser@someHost;
FLUSH PRIVILEGES;
```

Next, create the database by running the commands in `migrations/20200304T184500-create_database.sql`.
Then, create the tables by running the commands in `migrations/20200304T184700-create_tables.sql`.

## Usage
To start the app, run the following command from the project root directory.
The first variable is an async mode, where `threading` will run the development server.
Leaving it empty will allow for the default mode setting, and other modes are 
`gevent`, `eventlet` and `gevent_uwsgi`.
```
SIO_ASYNC_MODE=threading python3 -m src.server
```

To access the app in the browser, go to the url where the Flask server is running.
By default it will be `http://127.0.0.1:5000/`.


## Testing
The tests create a test database and do not alter the main database in any way.
To run the tests, run the following command from the project root directory
```
pytest
```
