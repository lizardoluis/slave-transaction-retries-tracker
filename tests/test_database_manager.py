import pytest
import mariadb
from source.slave_transaction_retries import RetryLogData
from source.database_manager import DatabaseManager

host = 'localhost'
port = 3306
user = 'lizardo'
password = ''
database = 'test'


@pytest.fixture
def db_manager():
    return DatabaseManager(host=host, port=port, user=user, password=password, database=database)


def teardown():
    conn = mariadb.connect(host=host, port=port, user=user, password=password, database=database)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE slave_transaction_retry_data;")
    conn.commit()
    cursor.close()
    conn.close()


def test_create_table(db_manager):
    db_manager.create_table()


def test_insert_retry_log_data(db_manager):
    log_data = [
        RetryLogData(timestamp='2023-05-01 12:00:00', thread_id='1', retry_number=1,
                     event_status='SUCCESS', event_number=1, event_group_size=1,
                     log_pos=100, gtid='0-1-2', query_id=100, retry_reason=0),
        RetryLogData(timestamp='2023-05-01 12:01:00', thread_id='2', retry_number=2,
                     event_status='FAILURE', event_number=2, event_group_size=2,
                     log_pos=200, gtid='0-1-3', query_id=200, retry_reason=1205),
        RetryLogData(timestamp='2023-05-01 12:02:00', thread_id='3', retry_number=3,
                     event_status=None, event_number=3, event_group_size=3,
                     log_pos=300, gtid='0-1-4', query_id=300, retry_reason=1213)
    ]
    db_manager.insert_retry_log_data(log_data)
