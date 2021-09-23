
import os
import string
import random
from flask import Flask
from flask_socketio import SocketIO, emit
import bcrypt
import configparser

from src.server_utils import (
    get_connection_and_cursor,
    authenticate_token,
    check_email_exists,
    check_channel_creator,
    get_channel_name,
    update_num_messages,
    set_read_counts,
    get_read_counts,
    get_num_replies
)

DB_NAME = os.getenv('CLEARDB_DB_NAME', 'lax_db')
DB_USERNAME = os.getenv('CLEARDB_USER', 'root')
DB_PASSWORD = os.getenv('CLEARDB_PASS', 'root')
DB_HOST = os.getenv('CLEARDB_HOST', '127.0.0.1')
PEPPER = "some_pepper"
SECRET_KEY = "some_secret_key"

config = configparser.ConfigParser()
read_res = config.read('secrets.cfg')
if read_res:
    DB_USERNAME = config['secrets']['DB_USERNAME']
    DB_PASSWORD = config['secrets']['DB_PASSWORD']
    DB_HOST = config['secrets']['DB_HOST']
    PEPPER = config['secrets']['PEPPER']
    SECRET_KEY = config['secrets']['SECRET_KEY']


# other async modes are 'eventlet', 'gevent', 'gevent_uwsgi' and 'threading'
# setting None lets the application choose the best option
ASYNC_MODE = os.getenv('SIO_ASYNC_MODE', None)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = SECRET_KEY

socketio = SocketIO(app, async_mode=ASYNC_MODE)



# ------------------------------ STATIC ROUTES ---------------------------------

@app.route('/')
@app.route('/<string:chnl_name>')
@app.route('/<string:chnl_name>/<int:msg_id>')
def index(chnl_name=None, msg_id=None):
    return app.send_static_file('index.html')

# -------------------------------- SOCKET ROUTES ----------------------------------

@socketio.on('signup')
def signup(json):
    email = json.get('custom_email', '')
    display_name = json.get('custom_display_name', '')
    password_hd = json.get('custom_password', '')

    email_exists = check_email_exists(email, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
    if email_exists:
        emit('signup_response', {'status': False})
        return

    password = (password_hd + PEPPER).encode('utf-8')
    seshn_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=35))
    
    connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)

    hashed = bcrypt.hashpw(password, bcrypt.gensalt())

    query = "INSERT into users (token, email, display_name, password) VALUES (%s, %s, %s, %s)"

    try:
        cursor.execute(query, (seshn_token, email, display_name, hashed,))
        connection.commit()
        emit('signup_response', {'status': True, 'session_token': seshn_token})
    except Exception as e:
        print(e)
        emit('signup_response', {'status': False})
    finally:
        cursor.close()
        connection.close()


@socketio.on('login')
def login(json):
    email = json.get('custom_email', '')
    password_hd = json.get('custom_password', '')
    password = (password_hd + PEPPER).encode('utf-8')

    connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)

    query = "SELECT password, token FROM users WHERE email=%s"

    try:
        cursor.execute(query, (email,))
        pass_db, seshn_token = cursor.fetchone()
        hashed = pass_db.encode('utf-8')

        if bcrypt.checkpw(password, hashed):
            emit('login_response', {'status': True, 'session_token': seshn_token})
            return

        emit('login_response', {'status': False})

    except Exception as e:
        print(e)
        emit('login_response', {'status': False})
    finally:
        cursor.close()
        connection.close()


@socketio.on('check_token')
def check_token(json):
    session_token = json.get('custom_session_token', '')
    auth = authenticate_token(session_token, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)

    if auth:
        emit('check_token_response', {'status': True})
        return
    emit('check_token_response', {'status': False})
    

@socketio.on('create')
def create(json):
    session_token = json.get('custom_session_token', '')
    channel_name = json.get('custom_channel_name', '')
    auth = authenticate_token(session_token, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)

    if auth:
        connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
        insert_query = "INSERT into channels (channel_name, creator_token, num_messages) VALUES (%s, %s, %s)"

        try:
            cursor.execute(insert_query, (channel_name, session_token, 0))
            connection.commit()
            emit('create_response', {'status': True}, broadcast=True)
            return
        except Exception as e:
            print(e)
            emit('create_response', {'status': False})
            return
        finally:
            cursor.close()
            connection.close()

    emit('create_response', {'status': False})


@socketio.on('delete')
def delete(json):
    session_token = json.get('custom_session_token', '')
    channel_name = json.get('custom_channel_name', '')
    auth = authenticate_token(session_token, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
    creator_valid = check_channel_creator(channel_name, session_token, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)

    if auth and creator_valid:
        connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
        del_queries = [
            "DELETE FROM channels WHERE channel_name=%s",
            "DELETE FROM messages WHERE channel_name=%s",
            "DELETE FROM read_counts WHERE channel_name=%s"
        ]

        try:
            for q in del_queries:
                cursor.execute(q, (channel_name,))
            
            connection.commit()
            emit('delete_response', {'status': True, 'del_channel': channel_name}, broadcast=True)
            return
        except Exception as e:
            print(e)
            emit('delete_response', {'status': False})
            return
        finally:
            cursor.close()
            connection.close()

    emit('delete_response', {'status': False})


@socketio.on('change_display_name')
def change_display_name(json):
    session_token = json.get('custom_session_token', '')
    display_name = json.get('custom_display_name', '')

    connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
    update_query = "UPDATE users SET display_name=%s WHERE token=%s"

    try:
        cursor.execute(update_query, (display_name, session_token, ))
        connection.commit()
        emit('change_display_name_response', {'status': True}, broadcast=True)
        return
    except Exception as e:
        print(e)
        emit('change_display_name_response', {'status': False})
        return
    finally:
        cursor.close()
        connection.close()


@socketio.on('change_email')
def change_email(json):
    session_token = json.get('custom_session_token', '')
    email = json.get('custom_email', '')

    connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
    update_query = "UPDATE users SET email=%s WHERE token=%s"

    try:
        cursor.execute(update_query, (email, session_token, ))
        connection.commit()
        emit('change_email_response', {'status': True})
        return
    except Exception as e:
        print(e)
        emit('change_email_response', {'status': False})
        return
    finally:
        cursor.close()
        connection.close()


@socketio.on('get_channels')
def get_channels(json):
    session_token = json.get('custom_session_token', '')
    auth = authenticate_token(session_token, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)

    if auth:
        connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
        select_query = "SELECT channel_name, num_messages, creator_token FROM channels"
        
        try:
            cursor.execute(select_query)
            channel_data = cursor.fetchall()

            count_dict = get_read_counts(session_token, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
            result = [
                {
                    'channel_name': x[0], 
                    'num_unread': x[1] - count_dict.get(x[0], 0),
                    'creator_token': x[2]
                } 
                for x in channel_data
            ]
            emit('get_channels_response', {'status': True, 'result': result})
            return
        except Exception as e:
            print(e)
            emit('get_channels_response', {'status': False})
            return
        finally:
            cursor.close()
            connection.close()

    emit('get_channels_response', {'status': False})


@socketio.on('post_messages')
def post_messages(json):
    session_token = json.get('custom_session_token', '')
    channel_name = json.get('custom_channel_name', '')
    message = json.get('custom_message', '')
    auth = authenticate_token(session_token, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)

    if auth:
        connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
        insert_query = "INSERT into messages (channel_name, author_token, body) VALUES (%s, %s, %s)"

        try:
            cursor.execute(insert_query, (channel_name, session_token, message))
            connection.commit()
            outcome = update_num_messages(channel_name, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
            if outcome:
                emit('post_messages_response', {'status': True, 'channel': channel_name}, broadcast=True)
                return
        except Exception as e:
            print(e)
            emit('post_messages_response', {'status': False})
            return
        finally:
            cursor.close()
            connection.close()

    emit('post_messages_response', {'status': False})


@socketio.on('get_messages')
def get_messages(json):
    session_token = json.get('custom_session_token', '')
    channel_name = json.get('custom_channel_name', '')
    auth = authenticate_token(session_token, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)

    if auth:
        connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
        select_msg_query = ("SELECT msg_id, author_token, body " +
                        "FROM messages WHERE reply_id is NULL AND channel_name=%s")
        select_names_query = "SELECT token, display_name from users"

        try:
            cursor.execute(select_msg_query, (channel_name,))
            msg_data = cursor.fetchall()

            cursor.execute(select_names_query)
            name_data = cursor.fetchall()

            name_dict = { x[0]: x[1] for x in name_data }
            result = [ {'msg_id': x[0], 
                        'num_replies': get_num_replies(x[0], DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST),
                        'display_name': name_dict[x[1]], 
                        'body': x[2]
                        } for x in msg_data ]

            set_count_bool = set_read_counts(session_token, channel_name, 
                                                len(msg_data), DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
            if set_count_bool:
                emit('get_messages_response', {'status': True, 'result': result})
                return
            
        except Exception as e:
            print(e)
            emit('get_messages_response', {'status': False})
            return
        finally:
            cursor.close()
            connection.close()

    emit('get_messages_response', {'status': False})


@socketio.on('post_reply')
def post_reply(json):
    session_token = json.get('custom_session_token', '')
    msg_id = json.get('custom_msg_id', '')
    message = json.get('custom_message', '')
    auth = authenticate_token(session_token, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
    channel_name = get_channel_name(msg_id, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)

    if auth:
        connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
        insert_query = "INSERT into messages (channel_name, reply_id, author_token, body) VALUES (%s, %s, %s, %s)"

        try:
            cursor.execute(insert_query, (channel_name, msg_id, session_token, message))
            connection.commit()
            emit('post_reply_response', {'status': True}, broadcast=True)
            return
        except Exception as e:
            print(e)
            emit('post_reply_response', {'status': False})
            return
        finally:
            cursor.close()
            connection.close()

    emit('post_reply_response', {'status': False})


@socketio.on('get_replies')
def get_replies(json):
    session_token = json.get('custom_session_token', '')
    msg_id = json.get('custom_msg_id', '')
    auth = authenticate_token(session_token, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
    channel_name = get_channel_name(msg_id, DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)

    if auth:
        connection, cursor = get_connection_and_cursor(DB_USERNAME, DB_NAME, DB_PASSWORD, DB_HOST)
        select_main_msg_query = "SELECT author_token, body FROM messages WHERE msg_id=%s"
        select_replies_query = "SELECT msg_id, author_token, body FROM messages WHERE reply_id=%s"
        select_names_query = "SELECT token, display_name from users"

        try:
            cursor.execute(select_main_msg_query, (msg_id,))
            main_msg_row = cursor.fetchone()

            cursor.execute(select_replies_query, (msg_id,))
            reply_data = cursor.fetchall()

            cursor.execute(select_names_query)
            names_data = cursor.fetchall()

            names_dict = { x[0]: x[1] for x in names_data }

            main_msg = {'display_name': names_dict[main_msg_row[0]], 'body': main_msg_row[1]}
            replies = [{'msg_id': x[0], 'display_name': names_dict[x[1]], 'body': x[2]} for x in reply_data] 
            emit('get_replies_response', {
                    'status': True,
                    'channel_name': channel_name,
                    'main_msg': main_msg,
                    'replies': replies
            })
            return
        except Exception as e:
            print(e)
            emit('get_replies_response', {'status': False})
            return
        finally:
            cursor.close()
            connection.close()

    emit('get_replies_response', {'status': False})



if __name__ == '__main__':
    socketio.run(app)
