class RetryLogData:
    def __init__(self, timestamp, thread_id, retry_number, event_status, 
                 event_number, event_group_size, log_pos, gtid, query_id, 
                 retry_reason=None):
        self.timestamp = timestamp
        self.thread_id = thread_id
        self.retry_number = retry_number[1:]
        self.event_status = event_status
        self.event_number = event_number
        self.event_group_size = event_group_size
        self.log_pos = log_pos
        self.gtid = gtid
        self.query_id = query_id
        self.retry_reason = retry_reason

    def __str__(self):
        return f"{self.timestamp},{self.thread_id},{self.retry_number},{self.event_status},{self.event_number},{self.event_group_size},{self.log_pos},{self.gtid},{self.query_id},{self.retry_reason}"

    def print_data(self):
        print(f"Timestamp: {self.timestamp}")
        print(f"Thread ID: {self.thread_id}")
        print(f"Retry Number: {self.retry_number}")
        print(f"Event status: {self.event_status}")
        print(f"Event Number: {self.event_number}")
        print(f"Event Group Size: {self.event_group_size}")
        print(f"Log Position: {self.log_pos}")
        print(f"GTID: {self.gtid}")
        print(f"Query ID: {self.query_id}")
        print(f"Retry Reason: {self.retry_reason}")