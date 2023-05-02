import re
import os

from pygtail import Pygtail
from slave_transaction_retries import RetryLogData


class LogParser:
    def __init__(self, log_file_path: str, parse_log_from_begining: bool):
        self.log_file_path = log_file_path
        if parse_log_from_begining:
            self.__delete_offset_file()

    def parse_log(self):
        self.parsed_lines = []

        for line in Pygtail(self.log_file_path):
            parsed_line = self.__parse_line(line)
            if parsed_line:
                self.parsed_lines.append(parsed_line)

        return self.parsed_lines if self.parsed_lines else []

    def __delete_offset_file(self):
        try:
            os.remove(f"{self.log_file_path}.offset")
        except FileNotFoundError:
            pass

    def __parse_line(self, line: str):
        regex = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(.*?)\] \[(.*?)\](?: \[(.*?)\])? event: (\d+) of (\d+)  log_pos: (\d+)  GTID: (\S+)  query_id: (\d+)(?:  (?:result|reason): (\d+))?'

        pattern = re.compile(regex)
        match = pattern.search(line)
        if match:
            timestamp = match.group(1)
            thread_id = match.group(2)
            retry_num = match.group(3)
            event_status = match.group(4)
            event_number = match.group(5)
            event_group_size = match.group(6)
            log_pos = match.group(7)
            gtid = match.group(8)
            query_id = match.group(9)
            retry_reason = match.group(10)

            log_data = RetryLogData(timestamp, thread_id, retry_num,
                                    event_status, event_number,
                                    event_group_size, log_pos,
                                    gtid, query_id, retry_reason)
            return log_data
        return None
