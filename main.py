"""The start point of the application which will handle the user input and will call the handler to execute the commands."""

from tools.handler import Handler
from tools.logger import Logger

handler = Handler(
    "/Users/razvanchichirau/Desktop/Programare-in-Python/SongStorage/appsettings.json"
)
try:
    handler.start()
    print(handler.help() + "\n")
    cmd = input(">>> ").strip()
    while cmd != "exit":
        if cmd == "help":
            print(handler.help() + "\n")
        else:
            is_valid, data = handler.valid_command(cmd)
            handler.handle(*data) if is_valid else print(
                f"Unknown command received ({cmd})"
            )
        cmd = input(">>> ").strip()
except Exception as err:
    handler.put_log(str(err).strip(), Logger.CRITICAL)
    print("A critical error occurred. Please check the logs.")
    exit(1)
finally:
    print("Closing application...")
    handler.stop()
