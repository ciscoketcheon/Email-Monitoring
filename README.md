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

## 🧰 Step 2: Prepare a Linux server as syslog receiver

### 1️⃣ Enable UDP/TCP reception

Edit the rsyslog configuration:
```bash
sudo nano /etc/rsyslog.conf
```

Uncomment or add these lines:
```bash
# UDP syslog reception
module(load="imudp")
input(type="imudp" port="514")

# TCP syslog reception (optional)
module(load="imtcp")
input(type="imtcp" port="514")
```

---

### 2️⃣ Create a log routing rule

Create a new file:
```bash
sudo nano /etc/rsyslog.d/60-cisco-esa.conf
```

Add:
```bash
# Put all ESA logs in their own file
if ($fromhost-ip == '10.10.10.10') then {
    /var/log/esa/mail.log
    stop
}
```

Replace `10.10.10.10` with your ESA’s management IP.

---

### 3️⃣ Create folder and set permissions
```bash
sudo mkdir -p /var/log/esa
sudo touch /var/log/esa/mail.log
sudo chown syslog:adm /var/log/esa/mail.log
```

---

### 4️⃣ Restart rsyslog
```bash
sudo systemctl restart rsyslog
```

---

### 5️⃣ Verify it’s listening
```bash
sudo netstat -anu | grep 514   # for UDP
sudo netstat -ant | grep 514   # for TCP
```

---

### 6️⃣ Verify logs arrive
Send a test from ESA or look for entries like:
```
Oct 15 12:10:32 ESA01 AMP_SCAN: MID 12345 submitted file SHA256=abcd... awaiting verdict
```

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

