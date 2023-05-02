# Slave transaction retries tracker

This tool was created for [SAMU-123](https://mariadbcorp.atlassian.net/browse/SAMU-123).
It parses the log file created for [SAMU-124](https://mariadbcorp.atlassian.net/browse/SAMU-124) and insert the data collected into a custom database system, which can be defined by the user. Three database views are created to allow the analysis of the data. They are described below.


## Modes of execution
### Continuos:

In this mode, the tool creates a daemon that continuosly parse the log for new entries. The interval of parsing scans can be defined by the user with the flag `--parsing-interval`. The execution can be interrupted with the `ctrl+c` command. This is the default mode. 

### Run once:

In this mode, the tool scans the log file only once, inserts the data into the database, and finishes the execution. This mode can be selected with the `--run-once` option. 


## Data parsed

The data are collected from the log file created for [SAMU-124](https://mariadbcorp.atlassian.net/browse/SAMU-124). 

The log have the following format of entries: 

```
2023-04-20 14:36:13 [T24] [R1] [SUCCESS] event: 2 of 2  log_pos: 1663  GTID: 2-1-2  query_id: 327  result: 0
2023-04-20 14:36:15 [T24] [R1] event: 2 of 2  log_pos: 1863  GTID: 0-1-4  query_id: 333  reason: 1205
2023-04-20 14:36:17 [T24] [R2] event: 2 of 2  log_pos: 1863  GTID: 0-1-4  query_id: 335  reason: 1205
2023-04-20 14:36:19 [T24] [R3] event: 2 of 2  log_pos: 1863  GTID: 0-1-4  query_id: 337  reason: 1205
2023-04-20 14:36:21 [T24] [R4] event: 2 of 2  log_pos: 1863  GTID: 0-1-4  query_id: 339  reason: 1205
2023-04-20 14:36:23 [T24] [R4] [FAILURE] event: 2 of 2  log_pos: 1863  GTID: 0-1-4  query_id: 341  result: 1205
```

The data collected are: 
```
1. 2023-04-20 13:07:49  timestamp
2. [T24]		        thread ID
3. [R1]		            retry number
4. event: 2 of 2	    failed event and the number of events in group to retry
5. log_pos: 1663	    log_pos in master binlog
6. GTID: 2-1-2	        GTID
7. query_id: 327	    Query ID
8. reason: 1205	        retry reason (failed event error code)
```

## Database

The tool must receive as command line arguments the credentials (host, port, user, password and schema) to access a MariaDB database system. 

When started, the tool creates in this database a table named `slave_transaction_retry_data` that is used to store all the data parsed from the [log of transactions retry](https://github.com/mariadb-corporation/mariadb-samurai/commit/3a06c645e6f27fae7e746e83dc93e98164a781c7). A different name can be specified for the table with the flag `--table`. 

To allow the analysis of data, three views are also created automatically (it can be deactivated with the flat `--no-views`). 


### View 1 - retries_of_active_threads

This view shows the current retry count per active thread. 

```
CREATE VIEW IF NOT EXISTS retries_of_active_threads AS
    SELECT t1.thread_id, t1.retry_number as current_retry_count
    FROM slave_transaction_retry_data t1
    LEFT JOIN slave_transaction_retry_data t2
        ON t1.thread_id = t2.thread_id
        AND t1.timestamp < t2.timestamp
    WHERE t2.thread_id IS NULL;
```

```
┌───────────┬─────────────────────┐
│ thread_id │ current_retry_count │
├───────────┼─────────────────────┤
│ T26       │ 1                   │
│ T27       │ 2                   │
│ T24       │ 1                   │
│ T28       │ 1                   │
└───────────┴─────────────────────┘
```


### View 2 - retries_per_error

This view shows the number of retries per error reason. Errors are for example 1205 (Lock wait timeout exceeded) or 1213 (Deadlock found when trying to get lock) etc.

```
CREATE VIEW IF NOT EXISTS retries_per_error AS
    SELECT retry_reason, count(retry_reason) as number_of_retries
    FROM slave_transaction_retry_data
    WHERE retry_reason <> 0
    GROUP BY retry_reason;
```
```
┌──────────────┬───────────────────┐
│ retry_reason │ number_of_retries │
├──────────────┼───────────────────┤
│ 1205         │ 9                 │
│ 4711         │ 1                 │
└──────────────┴───────────────────┘
```


### View 3 - retries_per_timestamp

This view counts the number of retries per timestamp with minute precision. It can be used to create histograms to identify in which period of the day the retries are occurring most. 

```
CREATE VIEW IF NOT EXISTS retries_per_time_of_day AS
    SELECT DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i') AS time_of_day, COUNT(*) AS number_of_retries
    FROM slave_transaction_retry_data
    GROUP BY time_of_day;
```

```
┌──────────────────┬───────────────────┐
│ timestamp        │ number_of_retries │
├──────────────────┼───────────────────┤
│ 2023-04-20 14:34 │ 4                 │
│ 2023-04-20 15:36 │ 1                 │
│ 2023-04-20 16:37 │ 7                 │
└──────────────────┴───────────────────┘
```

## Requirements

- Python 3.10
- MariaDB Samurai with [SAMU-124](https://github.com/mariadb-corporation/mariadb-samurai/commit/3a06c645e6f27fae7e746e83dc93e98164a781c7) with the  parameter `log_slave_retries=/path/to/file.log` set in the configuration file. 

Required Python libraries can be installed with the command:

```
python3 -m python3 -m pip install -r requirements.txt 
```

## Usage

```
python3 source/tracker.py [-h] -f LOG_FILE -H HOST -u USER [-p PASSWORD] -P PORT -s SCHEMA [-t TABLE] [-i PARSING_INTERVAL] [-b] [-r] [-T] [-v]
```

### Options:
```
  -h, --help            show this help message and exit
  -f LOG_FILE, --log-file LOG_FILE
                        log file to parse
  -H HOST, --host HOST  database hostname or IP address
  -u USER, --user USER  database username
  -p PASSWORD, --password PASSWORD
                        database password (default: )
  -P PORT, --port PORT  database port to connect to
  -s SCHEMA, --schema SCHEMA
                        database schema to create table into
  -t TABLE, --table TABLE
                        database table to store the collected retry statistics (default: slave_transaction_retry_data)
  -i PARSING_INTERVAL, --parsing-interval PARSING_INTERVAL
                        log parsing interval in seconds (default: 10)
  -b, --parse-log-from-begining
                        parse log from the begining (default: False)
  -r, --run-once        run daemon only once and stop execution (default: False)
  -T, --truncate        truncate the table data for clean start (default: False)
  -v, --verbose         verbose execution (default: False)
  -n, --no-views        do not create the database views (default: False)
```

## Example

In the following example, the tool will parse the log `tests/data/retry.log` only once and store the data in the database running in the localhost. 

```
python3 source/tracker.py --host localhost --port 3306 --user myuser --password mypass --schema test --log-file tests/data/retry.log --verbose --run-once
```
