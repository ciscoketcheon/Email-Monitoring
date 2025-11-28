
import subprocess
import time
import os
import sys

# Variables for easy modification
SMTP_SERVER = "x.x.x.x"
SMTP_PORT = 25
SENDER_EMAIL = "monitoring@xxxxxx.com"
RECIPIENT_EMAIL = "soc@xxxxxxxxxxxx.com"
RETRY_LIMIT = 1   # retry interval, 0 for immediate trigger on error
CHECK_INTERVAL_SECONDS = 300  # 5 minutes
USE_SWAKS = True  # Set to False to use Python smtplib instead
SNMP_TRAP_COMMAND = "/usr/bin/snmptrap"  # Path to snmptrap command
SNMP_TRAP_DEST = "x.x.x.x"  # SNMP manager IP
SNMP_COMMUNITY = "public"
SNMP_TRAP_OID = "1.3.6.1.4.1.8072.2.3.0.1"  # Example OID for email failure trap

def send_email_with_swaks():
    cmd = [
        "swaks",
        "--to", RECIPIENT_EMAIL,
        "--from", SENDER_EMAIL,
        "--server", SMTP_SERVER,
        "--port", str(SMTP_PORT),
        "--timeout", "10"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def send_email_with_smtplib():
    import smtplib
    from email.message import EmailMessage

    msg = EmailMessage()
    msg.set_content("Test email for deliverability check.")
    msg["Subject"] = "Deliverability Check"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.send_message(msg)
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

def send_snmp_trap():
    cmd = [
        SNMP_TRAP_COMMAND,
        "-v", "2c",
        "-c", SNMP_COMMUNITY,
        SNMP_TRAP_DEST,
        "",  # empty agent address
        SNMP_TRAP_OID,
        "1.3.6.1.2.1.1.1.0",  # example OID (sysDescr)
        "s",  # type string
        "Email deliverability check failed after retries"
    ]
    try:
        subprocess.run(cmd, check=True)
        print("SNMP trap sent.")
    except Exception as e:
        print(f"Failed to send SNMP trap: {e}")


def check_email_deliverability():
    failure_count = 0
    while True:
        if USE_SWAKS:
            success, output = send_email_with_swaks()
        else:
            success, output = send_email_with_smtplib()

        if success:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Email sent successfully.")
            failure_count = 0  # reset failure count on success
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Email send failed: {output}")
            failure_count += 1
            if failure_count > RETRY_LIMIT:
                print("Failure limit exceeded, sending SNMP trap.")
                send_snmp_trap()
                failure_count = 0  # reset after trap sent

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    check_email_deliverability()

