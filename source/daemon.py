import time

from database_manager import DatabaseManager
from log_parser import LogParser


class LogReaderDaemon:
    def __init__(self, interval: int, run_once: bool, verbose: bool,
                 database_manager: DatabaseManager,
                 log_parser: LogParser):
        self.interval = interval
        self.shall_run = True
        self.run_once = run_once
        self.database_manager = database_manager
        self.log_parser = log_parser
        self.count_iterations = 0
        self.verbose = verbose

    def start(self):
        try:
            print("Log reader daemon started at:", time.ctime())
            self.database_manager.create_table()
            self.database_manager.create_views()
            while self.shall_run:
                self.count_iterations += 1
                self.process()
                if self.run_once:
                    print("Log reader daemon ran once and finished.")
                    return
                time.sleep(self.interval)
            print(f"Log reader daemon stopped by stop request after {self.count_iterations} iterations.")
        except KeyboardInterrupt:
            print(f" Log reader daemon stopped by user interrupt after {self.count_iterations} iterations.")

    def stop(self):
        self.shall_run = False

    def process(self):
        log_data = self.log_parser.parse_log()
        number_of_log_entries = len(log_data)
        if number_of_log_entries > 0:
            self.database_manager.insert_retry_log_data(log_data)
        if self.verbose:
            print(f"Log reader daemon collected {number_of_log_entries} {'entries' if number_of_log_entries > 1 else 'entry'} at:", time.ctime())