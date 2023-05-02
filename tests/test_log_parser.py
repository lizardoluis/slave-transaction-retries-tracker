import os
from source.log_parser import LogParser


def setup():
    remove_offset_file_if_exists()


def teardown():
    remove_offset_file_if_exists()


def test_parser():
    parser = LogParser("tests/data/retry.log")
    parsed_lines = parser.parse_log()
    output = ["2023-04-20 14:36:13,T24,R1,SUCCESS,2,2,1663,2-1-2,327,0",
              "2023-04-20 14:36:15,T24,R1,None,2,2,1863,0-1-4,333,1205",
              "2023-04-20 14:36:17,T24,R2,None,2,2,1863,0-1-4,335,1205",
              "2023-04-20 14:36:19,T24,R3,None,2,2,1863,0-1-4,337,1205",
              "2023-04-20 14:36:21,T24,R4,None,2,2,1863,0-1-4,339,1205",
              "2023-04-20 14:36:23,T24,R4,FAILURE,2,2,1863,0-1-4,341,1205"]
    for i in range(len(parsed_lines)):
        assert str(parsed_lines[i]) == output[i]


def remove_offset_file_if_exists():
    file = 'retry.log.offset'  
    location = "tests/data/"
    path = os.path.join(location, file)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
