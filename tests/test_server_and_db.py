import pytest
import mysql.connector
import src.server as server
import configparser
from src.sql_commands import CRT_DB, CRT_USERS, CRT_CHANNELS, CRT_MESSAGES, CRT_COUNTS


DB_USERNAME = 'root'
DB_PASSWORD = 'root'
DB_HOST = '127.0.0.1'

config = configparser.ConfigParser()
read_res = config.read('secrets.cfg')
if read_res:
  DB_USERNAME = config['secrets']['DB_USERNAME']
  DB_PASSWORD = config['secrets']['DB_PASSWORD']
  DB_HOST = config['secrets']['DB_HOST']

TEST_DB_NAME = 'lax_test_db'

CRT_DB_REPLACED = CRT_DB.replace('DB_NAME_REPLACE', TEST_DB_NAME)


@pytest.fixture(autouse=False)
def setup_and_delete_db(monkeypatch):
  monkeypatch.setattr(server, 'DB_NAME', TEST_DB_NAME)

  # create db
  connection = mysql.connector.connect(user=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST)
  cursor = connection.cursor()
  cursor.execute(CRT_DB_REPLACED)
  cursor.execute(f"use {TEST_DB_NAME}")
  for cmd in [CRT_USERS, CRT_CHANNELS, CRT_MESSAGES, CRT_COUNTS]:
    cursor.execute(cmd)
  
  yield connection, cursor

  # delete db when test ends
  cursor.execute(f"drop database {TEST_DB_NAME}")
  connection.commit()
  cursor.close()
  connection.close()


def signup_and_get_client():
  client = server.socketio.test_client(server.app)
  client.emit('signup', {
    'custom_email': 'email333@fake.com', 
    'custom_display_name': 'fake_name', 
    'custom_password': 'pass123'
  })
  return client


def get_token_from_client(client):
  got = client.get_received()
  assert len(got) == 1
  got_token = got[0]['args'][0]['session_token']
  return got_token


def create_based_on_client(client, token, channel):
  client.emit('create', {
    'custom_session_token': token, 
    'custom_channel_name': channel
  })


def get_token_and_create_channel(client, chnl):
  got_token = get_token_from_client(client)
  create_based_on_client(client, got_token, chnl)
  return got_token


def post_msg_based_on_client(client, token, chnl, msg):
  client.emit('post_messages', {
    'custom_session_token': token,
    'custom_channel_name': chnl,
    'custom_message': msg
  })


def post_reply_based_on_client(client, token, msg_id, msg):
  client.emit('post_reply', {
    'custom_session_token': token, 
    'custom_msg_id': msg_id, 
    'custom_message': msg
  })


# --------- Tests --------- 


def test_authenticate_token(setup_and_delete_db):
  got = server.authenticate_token('fake_token123', DB_USERNAME, TEST_DB_NAME, DB_PASSWORD, DB_HOST)
  assert got == False


def test_email_exists(setup_and_delete_db):
  got = server.check_email_exists('FakeEmailskoxmq9@gfh.j', DB_USERNAME, TEST_DB_NAME, DB_PASSWORD, DB_HOST)
  assert got == False


def test_channel_creator(setup_and_delete_db):
  got = server.check_channel_creator('chanlx2z', 'faketok890', DB_USERNAME, TEST_DB_NAME, DB_PASSWORD, DB_HOST)
  assert got == False


def test_get_channel_name(setup_and_delete_db):
  got = server.get_channel_name('1337', DB_USERNAME, TEST_DB_NAME, DB_PASSWORD, DB_HOST)
  assert got == ""


def test_update_num_msgs(setup_and_delete_db):
  got = server.update_num_messages('chanlx2z', DB_USERNAME, TEST_DB_NAME, DB_PASSWORD, DB_HOST)
  assert got == True


def test_set_read_counts(setup_and_delete_db):
  got = server.set_read_counts('tk987654', 'ch4321', '3', DB_USERNAME, TEST_DB_NAME, DB_PASSWORD, DB_HOST)
  assert got == True


def test_get_read_counts(setup_and_delete_db):
  got = server.get_read_counts('tk7654', DB_USERNAME, TEST_DB_NAME, DB_PASSWORD, DB_HOST)
  assert got == {}


def test_get_num_replies(setup_and_delete_db):
  got = server.get_num_replies('1337', DB_USERNAME, TEST_DB_NAME, DB_PASSWORD, DB_HOST)
  assert got == 0


def test_check_token(setup_and_delete_db):
  client = server.socketio.test_client(server.app)
  client.emit('check_token', {'custom_session_token': 'fake_token123'})
  got = client.get_received()
  assert len(got) == 1
  assert got[0]['args'][0] == {'status': False}


def test_signup(setup_and_delete_db):
  client = signup_and_get_client()
  got = client.get_received()
  assert len(got) == 1
  assert got[0]['args'][0]['status'] == True


def test_login(setup_and_delete_db):
  client = signup_and_get_client()
  client.emit('login', {
    'custom_email': 'email333@fake.com',
    'custom_password': 'pass123'
  })
  got = client.get_received()
  assert len(got) == 2
  assert got[1]['args'][0]['status'] == True


def test_create(setup_and_delete_db):
  client = signup_and_get_client()
  client_other = server.socketio.test_client(server.app)
  
  _ = get_token_and_create_channel(client, 'channel_a')
  
  got = client.get_received()
  assert len(got) == 1
  assert got[0]['args'][0]['status'] == True
  got_other = client_other.get_received()
  assert len(got_other) == 1
  assert got_other[0]['args'][0]['status'] == True


def test_delete(setup_and_delete_db):
  client_other = server.socketio.test_client(server.app)
  client = signup_and_get_client()

  got_token = get_token_and_create_channel(client, 'channel_a')

  client.emit('delete', {
    'custom_session_token': got_token, 
    'custom_channel_name': 'channel_a'
  })
  got = client.get_received()
  assert len(got) == 2
  assert got[1]['args'][0]['status'] == True
  got_other = client_other.get_received()
  assert len(got_other) == 2
  assert got_other[1]['args'][0]['status'] == True


def test_change_display_name(setup_and_delete_db):
  client = signup_and_get_client()
  got_token = get_token_from_client(client)
  client.emit('change_display_name', {
    'custom_session_token': got_token, 
    'custom_display_name': 'MY_NEW_NAME'
  })
  got = client.get_received()
  assert len(got) == 1
  assert got[0]['args'][0]['status'] == True


def test_change_email(setup_and_delete_db):
  client = signup_and_get_client()
  got_token = get_token_from_client(client)
  client.emit('change_email', {
    'custom_session_token': got_token, 
    'custom_email': 'new@email.com'
  })
  got = client.get_received()
  assert len(got) == 1
  assert got[0]['args'][0]['status'] == True


def test_get_channels(setup_and_delete_db):
  client = signup_and_get_client()
  got_token = get_token_and_create_channel(client, 'channel_a')

  client.emit('get_channels', {
    'custom_session_token': got_token
  })
  got = client.get_received()
  assert len(got) == 2
  assert got[1]['args'][0]['status'] == True
  exp_dict = {'channel_name': 'channel_a', 
              'num_unread': 0, 
              'creator_token': got_token
  }
  assert got[1]['args'][0]['result'][0] == exp_dict


def test_post_messages(setup_and_delete_db):
  client_other = server.socketio.test_client(server.app)
  client = signup_and_get_client()
  got_token = get_token_and_create_channel(client, 'channel_a')
  post_msg_based_on_client(client, got_token, 'channel_a', 'a_message')

  exp_dict = {'status': True, 'channel': 'channel_a'}
  got = client.get_received()
  assert len(got) == 2
  assert got[1]['args'][0] == exp_dict
  got_other = client_other.get_received()
  assert len(got_other) == 2
  assert got_other[1]['args'][0] == exp_dict


def test_get_messages(setup_and_delete_db):
  client = signup_and_get_client()
  got_token = get_token_and_create_channel(client, 'channel_a')
  post_msg_based_on_client(client, got_token, 'channel_a', 'a_message')

  client.emit('get_messages', {
    'custom_session_token': got_token,
    'custom_channel_name': 'channel_a'
  })
  exp_dict = {'status': True, 
              'result': [{'msg_id': 1, 
                          'num_replies': 0, 
                          'display_name': 'fake_name', 
                          'body': 'a_message'}]
  }
  got = client.get_received()
  assert len(got) == 3
  assert got[2]['args'][0] == exp_dict


def test_post_reply(setup_and_delete_db):
  client_other = server.socketio.test_client(server.app)
  client = signup_and_get_client()
  got_token = get_token_and_create_channel(client, 'channel_a')
  post_msg_based_on_client(client, got_token, 'channel_a', 'a_message')
  post_reply_based_on_client(client, got_token, 1, 'a_reply')

  got = client.get_received()
  assert len(got) == 3
  assert got[2]['args'][0]['status'] == True
  got_other = client_other.get_received()
  assert len(got_other) == 3
  assert got_other[2]['args'][0]['status'] == True


def test_get_replies(setup_and_delete_db):
  client = signup_and_get_client()
  got_token = get_token_and_create_channel(client, 'channel_a')
  post_msg_based_on_client(client, got_token, 'channel_a', 'a_message')
  post_reply_based_on_client(client, got_token, 1, 'a_reply')

  client.emit('get_replies', {
    'custom_session_token': got_token,
    'custom_msg_id': 1
  })
  exp_dict = {'status': True, 
              'channel_name': 'channel_a', 
              'main_msg': {'display_name': 'fake_name', 'body': 'a_message'}, 
              'replies': [{'msg_id': 2, 'display_name': 'fake_name', 'body': 'a_reply'}]
  }
  got = client.get_received()
  assert len(got) == 4
  assert got[3]['args'][0] == exp_dict
