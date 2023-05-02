import argparse

from database_manager import DatabaseManager
from daemon import LogReaderDaemon
from log_parser import LogParser


def parse_arguments():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-f', '--log-file', action='store',
                        help='log file to parse', type=str,
                        required=True, default=argparse.SUPPRESS)

    parser.add_argument('-H', '--host', action='store',
                        help='database hostname or IP address', type=str,
                        required=True, default=argparse.SUPPRESS)

    parser.add_argument('-u', '--user', action='store',
                        help='database username', type=str,
                        required=True, default=argparse.SUPPRESS)

    parser.add_argument('-p', '--password', action='store',
                        help='database password', type=str,
                        default="")

    parser.add_argument('-P', '--port', action='store',
                        help='database port to connect to', type=int,
                        required=True, default=argparse.SUPPRESS)

    parser.add_argument('-s', '--schema', action='store',
                        help='database schema to create table into', type=str,
                        required=True, default=argparse.SUPPRESS)

    parser.add_argument('-t', '--table', action='store',
                        help='database table to store the collected retry statistics', type=str,
                        default="slave_transaction_retry_data")

    parser.add_argument('-i', '--parsing-interval', action='store',
                        help='log parsing interval in seconds',
                        default=10, type=int)

    parser.add_argument('-b', "--parse-log-from-begining", action="store_true",
                        help="parse log from the begining",
                        default=False)

    parser.add_argument('-r', "--run-once", action="store_true",
                        help="run daemon only once and stop execution",
                        default=False)

    parser.add_argument('-T', "--truncate", action="store_true",
                        help="truncate the table data for clean start",
                        default=False)

    parser.add_argument('-v', "--verbose", action="store_true",
                        help="verbose execution",
                        default=False)
    
    parser.add_argument('-n', "--no-views", action="store_true",
                        help="do not create the database views",
                        default=False)

    global ARGS
    ARGS = parser.parse_args()


if __name__ == '__main__':
    parse_arguments()

    log_parser = LogParser(ARGS.log_file, ARGS.parse_log_from_begining)

    database_manager = DatabaseManager(host=ARGS.host,
                                       port=ARGS.port,
                                       user=ARGS.user,
                                       password=ARGS.password,
                                       schema=ARGS.schema,
                                       table=ARGS.table,
                                       truncate=ARGS.truncate,
                                       verbose=ARGS.verbose,
                                       no_views=ARGS.no_views)

    daemon = LogReaderDaemon(interval=ARGS.parsing_interval,
                             run_once=ARGS.run_once,
                             verbose=ARGS.verbose,
                             database_manager=database_manager,
                             log_parser=log_parser)
    daemon.start()
