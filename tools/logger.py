"""Module responsible for logging the application's activity."""
import os
import threading
import time
from queue import Queue
from datetime import datetime


class Logger(threading.Thread):
    """A class which provides static methods to log the application's activity."""

    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3

    def __init__(self, log_path: str, queue: Queue):
        """
        Initializes the Logger class.

            - log_path: str - the path to the log file
            - queue: Queue - the queue object

        Returns: None
        """
        super().__init__()
        if not isinstance(log_path, str):
            raise TypeError("log_path must be a string")
        if not os.path.isabs(log_path):
            raise ValueError("log_path must be an absolute or valid path")
        self.log_path = log_path
        self.queue = queue
        self._stop = threading.Event()

    def log(self, msg: str, level: int) -> str:
        """
        Logs the message to the log file.
        The message is formatted as follows: (<timestamp>)[<severity>] - <msg>

            - msg: str - the message to be logged
            - level: int - the severity level of the message

        Returns: str - the formatted message
        """

        timestamp = datetime.now().strftime("(%d/%m/%Y, %H:%M:%S)")

        severity = "[INFO]"
        match level:
            case Logger.WARNING:
                severity = "[WARNING]"
            case Logger.ERROR:
                severity = "[ERROR]"
            case Logger.CRITICAL:
                severity = "[CRITICAL]"
            case _:
                pass

        return f"{timestamp}{severity} - {msg}\n"

    def stop(self) -> None:
        """Stops the logger thread."""
        self._stop.set()

    def run(self) -> None:
        """Starts the execution of the logger thread."""
        with open(self.log_path, "w") as file:
            file.write(self.log("Logger initialized successfully.", Logger.INFO))
            while not self._stop.is_set():
                if self.queue.empty():
                    time.sleep(0.2)
                    continue
                msg, level = self.queue.get()
                file.write(self.log(msg, level))
            while not self.queue.empty():
                msg, level = self.queue.get()
                file.write(self.log(msg, level))
            file.flush()
