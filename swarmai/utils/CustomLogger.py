import logging
import json
from pathlib import Path

class CustomFormatter(logging.Formatter):
    def format(self, record):
        """record.__dict__ looks like:
        {'name': 'SwarmLogger',
        'msg': {'message': "Created 2 agents with roles: ['python developer' 'python developer']"}, 'args': (), 'levelname': 'INFO', 'levelno': 20, 'pathname': 'D:\\00Repos\\GPT-Swarm\\tests\\..\\swarmai\\Swarm.py', 'filename': 'Swarm.py', 'module': 'Swarm', 'exc_info': None, 'exc_text': None, 'stack_info': None, 'lineno': 203, 'funcName': 'log', 'created': 1681553727.7010381, 'msecs': 701.038122177124, 'relativeCreated': 1111.7806434631348, 'thread': 46472, 'threadName': 'MainThread', 'processName': 'MainProcess', 'process': 65684}
        """
        record_content = record.msg
        if "message" in record_content:
            message = record_content["message"]
        else:
            message = record_content
        
        if 'agent_id' not in record_content:
            record_content["agent_id"] = -1
        if 'agent_type' not in record_content:
            record_content["agent_type"] = -1
        if 'cycle' not in record_content:
            record_content["cycle"] = -1
        if 'step' not in record_content:
            record_content["step"] = "swarm"

        log_data = {
            'time': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'agent_id': record_content["agent_id"],
            'agent_type': record_content["agent_type"],
            'cycle': record_content["cycle"],
            'step': record_content["step"],
            'message': message
        }
        return json.dumps(log_data)

class CustomLogger(logging.Logger):
    def __init__(self, log_folder):
        super().__init__("SwarmLogger")
        self.log_folder = log_folder
        self.log_folder.mkdir(parents=True, exist_ok=True)

        log_file = f"{self.log_folder}/swarm.json"
        # write empty string to the log file to clear it
        with open(log_file, "w") as f:
            f.write("")
            f.close()

        # Create a custom logger instance and configure it
        self.log_file = log_file
        self.log_folder = self.log_folder
        self.setLevel(logging.DEBUG)
        formatter = CustomFormatter()

        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.addHandler(ch)

        # # Add a CSV file handler to log messages in CSV format
        # csv_file = f"{self.log_folder}/swarm.csv"
        # csv_formatter = logging.Formatter('%(asctime)s,%(levelname)s,%(agent_id)s,%(agent_type)s,%(cycle)s,%(step)s,%(message)s')
        # csv_handler = logging.FileHandler(csv_file)
        # csv_handler.setFormatter(csv_formatter)
        # csv_handler.setLevel(logging.DEBUG)
        # self.addHandler(csv_handler)