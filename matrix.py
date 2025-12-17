import random
import string
import time
import sys
import os

os.system("")  # enable ANSI colors on Windows

GREEN = "\033[92m"
RESET = "\033[0m"

def matrix_burst(lines=55, width=70):
    for _ in range(lines):
        line = "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(width)
        )
        print(GREEN + line + RESET)
        sys.stdout.flush()
        time.sleep(0.025)