import mariadb
import sys


class DatabaseManager:
    def __init__(self, host, port, user, password, schema, table, truncate,
                 verbose, no_views):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.schema = schema
        self.conn = None
        self.table_name = table
        self.truncate = truncate
        self.verbose = verbose
        self.no_views = no_views
        if truncate:
            self.__truncate_table()

    def connect(self):
        try:
            self.conn = mariadb.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.schema
            )
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

    def create_table(self):
        self.connect()
        cursor = self.conn.cursor()
        statement = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            timestamp DATETIME,
            thread_id VARCHAR(20),
            retry_number INT,
            event_status VARCHAR(20),
            event_number INT,
            event_group_size INT,
            log_pos BIGINT,
            gtid VARCHAR(50),
            query_id BIGINT,
            retry_reason INT
        );"""
        self.__verbose_print(f"Creating table \'{self.schema}.{self.table_name}\'")
        try:
            cursor.execute(statement)
            self.conn.commit()
            cursor.close()
            self.conn.close()
        except mariadb.Error as e:
            print(f"Error while creating the database table \'{self.schema}.{self.table_name}\': {e}")
            cursor.close()
            self.conn.close()
            sys.exit(1)

    def insert_retry_log_data(self, log_data: list):
        self.connect()
        cursor = self.conn.cursor()

        query = f"""INSERT INTO {self.table_name} (timestamp,
            thread_id, retry_number, event_status, event_number,
            event_group_size, log_pos, gtid, query_id, retry_reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

        for retry_data in log_data:
            values = (retry_data.timestamp, retry_data.thread_id,
                      retry_data.retry_number, retry_data.event_status,
                      retry_data.event_number, retry_data.event_group_size,
                      retry_data.log_pos, retry_data.gtid,
                      retry_data.query_id, retry_data.retry_reason)
            cursor.execute(query, values)

        self.conn.commit()
        cursor.close()
        self.conn.close()

    def create_views(self):
        if not self.no_views:
            self.create_view("retries_of_active_threads",
                            """CREATE VIEW IF NOT EXISTS retries_of_active_threads AS
                                SELECT t1.thread_id, t1.retry_number as current_retry_count
                                FROM slave_transaction_retry_data t1
                                LEFT JOIN slave_transaction_retry_data t2
                                    ON t1.thread_id = t2.thread_id
                                    AND t1.timestamp < t2.timestamp
                                WHERE t2.thread_id IS NULL;""")

            self.create_view("retries_per_error",
                            """CREATE VIEW IF NOT EXISTS retries_per_error AS
                                SELECT retry_reason, count(retry_reason) AS number_of_retries
                                FROM slave_transaction_retry_data
                                WHERE retry_reason <> 0
                                GROUP BY retry_reason;""")

            self.create_view("retries_per_timestamp",
                            """CREATE VIEW IF NOT EXISTS retries_per_time_of_day AS
                                SELECT DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i') AS time_of_day, COUNT(*) AS number_of_retries
                                FROM slave_transaction_retry_data
                                GROUP BY time_of_day;""")

    def create_view(self, name: str, statement: str):
        self.connect()
        cursor = self.conn.cursor()
        self.__verbose_print(f"Creating view \'{name}\'")
        try:
            cursor.execute(statement)
            self.conn.commit()
            cursor.close()
            self.conn.close()
        except mariadb.Error as e:
            print(f"Error while creating view \'{name}\': {e}")
            cursor.close()
            self.conn.close()
            sys.exit(1)

    def __verbose_print(self, message: str):
        if self.verbose:
            print(message)

    def __truncate_table(self):
        self.connect()
        cursor = self.conn.cursor()
        statement = f"TRUNCATE TABLE {self.table_name}"
        self.__verbose_print(f"Truncating database table \'{self.schema}.{self.table_name}\'")
        try:
            cursor.execute(statement)
            self.conn.commit()
            cursor.close()
            self.conn.close()
        except mariadb.Error as e:
            print(f"Error while truncating the database table \'{self.schema}.{self.table_name}\': {e}")
            cursor.close()
            self.conn.close()
            sys.exit(1)
