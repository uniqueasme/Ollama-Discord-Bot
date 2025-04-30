import subprocess
import sys
import os

def run_bot():
    # Use sys.executable to ensure the same Python interpreter is used
    while True:
        process = subprocess.Popen([sys.executable, 'discord_bot.py'])
        process.wait()
        # If process exited with code 100, treat as reset, else break
        if process.returncode == 100:
            print('Bot reset requested, restarting...')
            continue
        else:
            print(f'Bot exited with code {process.returncode}, not restarting.')
            break

if __name__ == "__main__":
    run_bot()
