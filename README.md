Render Keep-Alive Monitor (Python + Selenium)

A lightweight Windows-friendly tool designed to keep Render-hosted applications awake and notify you when they go offline.
This project uses Python, Selenium, and a configurable JSON file, and can be compiled into a standalone .exe (via auto-py-to-exe or PyInstaller) to run on any machine without Python installed.

📌 What This Tool Does

Opens a Render application URL using Selenium

Checks if the page contains a specific text (ex: "I'm alive")

If the application is not alive:

Waits a configurable number of seconds

Tries again (configurable retry attempts)

If still offline:

Sends an email alert through SMTP

Exits immediately afterward

Designed to be executed periodically using Windows Task Scheduler

🔧 Key Features

🧩 Full configuration via config.json
URL, expected text, retry delays, and email settings are all customizable.

🏗 Auto-generates config file if missing
If config.json does not exist, the program creates one automatically with default values.

🖥 Works as a standalone .exe
Can be compiled so it runs on any machine without needing Python installed.

🕑 Single-run design
The script executes one check (with retries). Scheduling is handled externally (Windows Task Scheduler or cron).

📨 SMTP Email alerts
Sends an email when the application fails all retry attempts.

⚡ Runs headless via Selenium
No browser window pops up — everything happens silently.

📁 How It Works

Check if config.json exists

If not → create template and exit

Load configuration

Start Selenium and open the URL

Check if the page contains the expected text

If not:

Wait retry_delay_seconds

Retry up to max_attempts

If still offline:

Send email alert

Exit cleanly

📝 Example config.json
{
  "url": "https://vacationdiscordbot.onrender.com/",
  "expected_text": "I'm alive",
  "retry_delay_seconds": 60,
  "max_attempts": 2,
  "email": {
    "enabled": true,
    "smtp_host": "smtp.yourprovider.com",
    "smtp_port": 587,
    "smtp_username": "your@email.com",
    "smtp_password": "your_password",
    "from": "your@email.com",
    "to": [
      "dest1@email.com"
    ],
    "subject": "Vacation bot on Render is DOWN"
  }
}

🧰 Building the EXE

You can create a standalone executable using auto-py-to-exe:

pip install auto-py-to-exe
auto-py-to-exe


Configuration recommended:

Onefile mode → enabled

Console window → enabled (to see logs)

Add config.json → in Additional Files

This produces a single .exe that works on any Windows machine.

🕓 Recommended Usage (Windows Task Scheduler)

Open Task Scheduler

Create a Basic Task

Choose a trigger:

"Every 10 minutes"

Or any interval you prefer

Action: Start a program

Program/script: your_executable.exe

Start in: folder where the .exe and config.json are stored

This ensures Render applications stay alive and you get notified if they go offline.
