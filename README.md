# Email Deliverability Check Script

This script monitors email SMTP server deliverability and send notification trap on email service unavailabile. The monitoring period can be defined and default to 5min. The notification method is by SNMP trap. The script allows the use of python email library or swaks CLI tool. 
    

---

## 🔹 1. Prerequisites

Before running the email deliverability check script, ensure the following modules and tools are installed and configured:

- Python 3: The script requires Python 3 to run.
- Swaks (optional): If USE_SWAKS is set to True, install Swaks for SMTP testing. On Debian/Ubuntu, use:
   ```
   sudo apt-get install swaks
   ```
- Net-SNMP tools: The script sends SNMP traps using the snmptrap command. Install Net-SNMP utilities:
   ```
   sudo apt-get install snmp
   ```
- Python standard libraries: The script uses built-in modules such as subprocess, time, and optionally smtplib and email.message.
- Network access: Ensure the script can reach the SMTP server on port 25 and the SNMP trap destination IP on the network.


---

## ⚙️  2. Error Scenarios Captured

The script monitors email deliverability and handles these scenarios:

- Normal: Email is sent successfully; the script logs a success message and resets failure count.
- Error (Server Down): SMTP server is unreachable or down, causing connection failures; the script logs the failure and increments failure count.
- Brown-out (Port or Service Unavailable): SMTP server IP is reachable, but port 25 is not accepting connections; treated as a failure.
- Failure Limit Exceeded: When the number of consecutive failures exceeds RETRY_LIMIT, the script sends an SNMP trap alerting that email deliverability checks have failed, then resets failure count.
- SNMP Trap Sending Errors: The script handles errors when sending SNMP traps, such as missing snmptrap binary or invalid command arguments, and logs the error without crashing.


---

## 🧰 3. Deployment and Test Scenario

### Deployment

1. Configure Variables: Modify the following variables in the script as needed:

    - SMTP_SERVER: IP or hostname of the SMTP server.
    - SMTP_PORT: SMTP service port (default 25).
    - SENDER_EMAIL and RECIPIENT_EMAIL: Email addresses for the test message.
    - RETRY_LIMIT: Number of allowed consecutive failures before sending SNMP trap.
    - CHECK_INTERVAL_SECONDS: Interval between checks (default 300 seconds).
    - USE_SWAKS: Set to True to use Swaks, or False to use Python's smtplib.
    - SNMP_TRAP_COMMAND: Path to the snmptrap executable.
    - SNMP_TRAP_DEST: IP address of the SNMP trap receiver.
    - SNMP_COMMUNITY: SNMP community string.
    - SNMP_TRAP_OID: OID for the SNMP trap.

### Testing
1. Normal Case: Run the script with a reachable SMTP server accepting connections on port 25. Confirm output similar to:
   ```
   [YYYY-MM-DD HH:MM:SS] Email sent successfully.
   ```
2. Server Down Case: Test with an unreachable SMTP server IP or stopped mail service. The script should log failures and retry.

3. Brown-out Case: Test with the SMTP server IP reachable but port 25 closed or filtered. The script should detect failure and retry.

4. Failure Limit Exceeded: After exceeding retry limits, verify the script sends an SNMP trap. Confirm success message or error logs if snmptrap is missing or misconfigured.

5. SNMP Trap Command Validation: Ensure the send_snmp_trap() function uses the correct syntax with an empty agent address and valid variable bindings to avoid errors like "Bad variable type."

This documentation provides a clear overview for users to prepare, deploy, and test the email deliverability check script effectively, capturing key error scenarios and operational details.


---

## ⚙️ Step 3: Prepare this script

1. Modify the parameters near the top of `amp-notification.py`, such as:
   - Mail server IP or hostname  
   - Sender and recipient email addresses

---

## 🚀 Step 4: Make the script executable

Run manually to test:
```bash
sudo chmod +x /usr/local/bin/amp-notification.py
```

---

## 🧩 Step 5: (Optional) Run as a background service

Create a systemd unit file:
```bash
sudo nano /etc/systemd/system/esa-amp-watch.service
```

Add:
```ini
[Unit]
Description=Cisco ESA AMP log watcher
After=network.target

[Service]
ExecStart=/usr/local/bin/amp-notification.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now esa-amp-watch
```

---

## ✅ Result

Whenever ESA logs show a line like:

```
AMP file analysis initiated
```

The script sends an email notification to the designated security contact.

Example triggering event, file quarantined to AMP queue:-
![amp2](amp2.jpg)

Email action. 
![amp3](amp3.jpg)

---

### 📸 Screenshot
![amp4](amp4.jpg)


**Author:** [ciscoketcheon](https://github.com/ciscoketcheon)  
**License:** BSD3 

