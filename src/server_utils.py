
import mysql.connector


def get_connection_and_cursor(username, database, password, host):
    connection = mysql.connector.connect(user=username, database=database, password=password, host=host)
    cursor = connection.cursor()
    return connection, cursor


def authenticate_token(session_token, user, database, password, host):
    connection, cursor = get_connection_and_cursor(user, database, password, host)
    select_query = "SELECT password FROM users WHERE token=%s"

    try:
        cursor.execute(select_query, (session_token,))
        result = cursor.fetchone()
        if result:
            return True
        return False
    except Exception as e:
        print(e)
        return False
    finally:
        cursor.close()
        connection.close()


def check_email_exists(email, user, database, password, host):
    connection, cursor = get_connection_and_cursor(user, database, password, host)
    select_query = "SELECT 1 FROM users WHERE email=%s"

    try:
        cursor.execute(select_query, (email,))
        result = cursor.fetchone()
        if result:
            return True
        return False
    except Exception as e:
        print(e)
        return False
    finally:
        cursor.close()
        connection.close()


def check_channel_creator(c_name, token, user, database, password, host):
    connection, cursor = get_connection_and_cursor(user, database, password, host)
    select_query = "SELECT creator_token FROM channels WHERE channel_name=%s"

    try:
        cursor.execute(select_query, (c_name,))
        creator = cursor.fetchone()[0]
        if creator == token:
            return True
        return False
    except Exception as e:
        print(e)
        return False
    finally:
        cursor.close()
        connection.close()


def get_channel_name(msg_id, user, database, password, host):
    channel_name = ""

    connection, cursor = get_connection_and_cursor(user, database, password, host)
    select_query = "SELECT channel_name FROM messages WHERE msg_id=%s"

    try:
        cursor.execute(select_query, (msg_id,))
        channel_name = cursor.fetchone()[0]
        return channel_name
    except Exception as e:
        print(e)
        return ""
    finally:
        cursor.close()
        connection.close()


def update_num_messages(channel_name, user, database, password, host):
    connection, cursor = get_connection_and_cursor(user, database, password, host)
    update_query = "UPDATE channels SET num_messages = num_messages + 1 WHERE channel_name=%s"

    try:
        cursor.execute(update_query, (channel_name,))
        connection.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        cursor.close()
        connection.close()


def set_read_counts(token, channel_name, num_read, user, database, password, host):
    connection, cursor = get_connection_and_cursor(user, database, password, host)
    ins_dup_key_query = ("INSERT INTO read_counts (token, channel_name, num_read)"
                        + " VALUES (%s, %s, %s)"
                        + " ON DUPLICATE KEY UPDATE num_read=%s")

    try:
        cursor.execute(ins_dup_key_query, (token, channel_name, num_read, num_read,))
        connection.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        cursor.close()
        connection.close()


def get_read_counts(token, user, database, password, host):
    connection, cursor = get_connection_and_cursor(user, database, password, host)
    select_query = "SELECT channel_name, num_read FROM read_counts WHERE token=%s"

    try:
        cursor.execute(select_query, (token,))
        result = cursor.fetchall()
        count_dict = {x[0]: x[1] for x in result}
        return count_dict
    except Exception as e:
        print(e)
        return {}
    finally:
        cursor.close()
        connection.close()


def get_num_replies(msg_id, user, database, password, host):
    num_replies = 0

    connection, cursor = get_connection_and_cursor(user, database, password, host)
    select_query = "SELECT COUNT(reply_id) FROM messages WHERE reply_id=%s"

    try:
        cursor.execute(select_query, (msg_id,))
        num_replies = cursor.fetchone()[0]
        return num_replies
    except Exception as e:
        print(e)
        return 0
    finally:
        cursor.close()
        connection.close()
