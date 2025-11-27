import os
import sys
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException


# ================== CONFIG LOADER ==================


def get_base_dir() -> str:
    """
    Returns the folder where the script or .exe is located.
    Works for both normal Python and compiled exe.
    """
    if getattr(sys, "frozen", False):
        # When compiled (auto-py-to-exe / PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # When running as a normal .py
        return os.path.dirname(os.path.abspath(__file__))


def create_default_config_dict() -> dict:
    """Default template for config.json."""
    return {
        "url": "https://londublis.com/",
        "expected_text": "I'm alive",
        "retry_delay_seconds": 60,
        "max_attempts": 2,
        "email": {
            "enabled": False,
            "smtp_host": "mail.londublis.com",
            "smtp_port": 25,
            "smtp_username": "your@londublis.com",
            "smtp_password": "your_password",
            "from": "your@londublis.com",
            "to": ["dest1@email.com"],
            "subject": "Vacation bot on Render is DOWN"
        }
    }


def ensure_config_exists(config_filename: str = "config.json") -> str:
    """
    Ensures config file exists.
    If it doesn't, create a template and inform the user.
    Returns the full path to the config file.
    """
    base_dir = get_base_dir()
    config_path = os.path.join(base_dir, config_filename)

    if not os.path.exists(config_path):
        print("[WARN] Config file not found.")
        print(f"       Expected path: {config_path}")
        print("[INFO] Creating a template config.json...")

        config_data = create_default_config_dict()
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            print("[INFO] Template config.json created successfully.")
            print("       Please edit it with your URL, expected_text and email settings.")
        except Exception as e:
            print(f"[ERROR] Failed to create template config file: {e}")

        # For .exe usage, give the user a chance to see the message
        input("Press ENTER to exit...")
        sys.exit(1)

    return config_path


def load_config(config_filename: str = "config.json") -> dict:
    """
    Loads the configuration from config.json.
    If the file does not exist, it will be created with default values
    and the program will exit so the user can edit it.
    """
    config_path = ensure_config_exists(config_filename)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config


# ================== SELENIUM ==================


def create_webdriver() -> webdriver.Chrome:
    """Create a headless Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def is_app_alive(driver: webdriver.Chrome, url: str, expected_text: str) -> bool:
    """
    Open the URL and check if the expected text is present.
    """
    try:
        driver.get(url)
        page_source = driver.page_source
        return expected_text in page_source
    except WebDriverException as e:
        print(f"[ERROR] WebDriverException while loading page: {e}")
        return False


# ================== EMAIL ==================


def send_alert_email(email_config: dict, url: str, expected_text: str):
    """Send alert email using SMTP settings from config."""
    if not email_config.get("enabled", False):
        print("[INFO] Email alert is disabled in config.")
        return

    smtp_host = email_config["smtp_host"]
    smtp_port = email_config["smtp_port"]
    smtp_username = email_config["smtp_username"]
    smtp_password = email_config["smtp_password"]
    email_from = email_config["from"]
    email_to = email_config["to"]
    subject = email_config.get("subject", "Application is DOWN")

    msg = MIMEMultipart()
    msg["From"] = email_from
    msg["To"] = ", ".join(email_to)
    msg["Subject"] = subject

    body = (
        f"The application at {url} does not show the expected message: '{expected_text}'.\n"
        "Please check the Render service."
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        print("[INFO] Alert email sent successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to send alert email: {e}")


# ================== ONE-SHOT CHECK ==================


def run_single_check(config: dict):
    url = config["url"]
    expected_text = config["expected_text"]
    retry_delay_seconds = int(config.get("retry_delay_seconds", 60))
    max_attempts = int(config.get("max_attempts", 2))
    email_config = config.get("email", {})

    print("[INFO] Starting single check")
    print(f"       URL: {url}")
    print(f"       Expected text: {expected_text}")
    print(f"       Retry delay: {retry_delay_seconds} seconds")
    print(f"       Max attempts: {max_attempts}\n")

    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        driver = None
        try:
            driver = create_webdriver()
            print(f"[INFO] Attempt {attempts}/{max_attempts}...")
            alive = is_app_alive(driver, url, expected_text)

            if alive:
                print("[INFO] Application is alive ✅")
                return  # success, exit function

            print("[WARN] Application is NOT alive on this attempt.")

        except Exception as e:
            print(f"[ERROR] Unexpected error on attempt {attempts}: {e}")
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass

        # If we still have attempts left, wait before retrying
        if attempts < max_attempts:
            print(f"[INFO] Waiting {retry_delay_seconds} seconds before next attempt...\n")
            time.sleep(retry_delay_seconds)

    # If we reach here, all attempts failed
    print("[ERROR] Application still down after all attempts. Sending alert email...")
    send_alert_email(email_config, url, expected_text)


def main():
    try:
        config = load_config()
    except SystemExit:
        # Propagate sys.exit from ensure_config_exists
        return
    except Exception as e:
        print(f"[FATAL] Could not load config: {e}")
        input("Press ENTER to exit...")
        return

    run_single_check(config)


if __name__ == "__main__":
    main()
