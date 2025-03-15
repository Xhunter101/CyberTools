import requests

def ipinfo(ip):
    url = f"https://ipinfo.io/{ip}/json?token=10022defe09fcc"
    response = requests.get(url)
    data = response.json()
    loc = data.get('loc', '')
    
    # Split latitude and longitude
    latitude, longitude = loc.split(',') if loc else ('', '')
    
    return {
        'IP': data.get('ip', ''),
        'City': data.get('city', ''),
        'Region': data.get('region', ''),
        'Country': data.get('country', ''),
        'Latitude': latitude,
        'Longitude': longitude,
        'Org': data.get('org', ''),
        'Timezone': data.get('timezone', '')
    }

def vt_ip(ip):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headersList = {
        "x-apikey": "98817fa4b16a81038d1854dcbdc70a56e51e173919e6d7e6eb0817fc3303eddb" 
    }
    response = requests.get(url, headers=headersList)
    data = response.json()
    attributes = data.get("data", {}).get("attributes", {})
    return {
        'IP': ip,
        'Country': attributes.get('country', ''),
        'Continent': attributes.get('continent', ''),
        'ASN': attributes.get('asn', ''),
        'Regional Internet Registry': attributes.get('regional_internet_registry', ''),
        'AS Owner': attributes.get('as_owner', ''),
        'Network': attributes.get('network', ''),
        'Risk Score': attributes.get('last_analysis_stats', {}).get('malicious', 'N/A'),
        'Harmless': attributes.get('last_analysis_stats', {}).get('harmless', 'N/A')
    }

def ip2location(ip):
    url = f"https://api.ip2location.io?ip={ip}&format=json"
    response = requests.get(url)
    data = response.json()
    return {
        'IP': ip,
        'Country Code': data.get('country_code', ''),
        'Country': data.get('region_name', ''),
        'Region': data.get('region_name', ''),
        'City': data.get('city_name', ''),
        'Latitude': data.get('latitude', ''),
        'Longitude': data.get('longitude', ''),
        'ZIP Code': data.get('zip_code', ''),
        'Timezone': data.get('time_zone', ''),
        'ASN': data.get('asn', ''),
        'ISP': data.get('as', ''),
    }

def db_ip(ip):
    url = f"https://api.db-ip.com/v2/free/{ip}"
    response = requests.get(url)
    data = response.json()
    return {
        'IP': ip,
        'Country': data.get('countryName', ''),
        'Region': data.get('stateProv', ''),
        'Country Code': data.get('countryCode', ''),
        'City': data.get('city', '')
    }

def ipapi(ip):
    url = f"https://ipapi.co/{ip}/json"
    response = requests.get(url)
    data = response.json()
    return {
        'IP': ip,
        'City': data.get('city', ''),
        'Region': data.get('region', ''),
        'Region Code': data.get('region_code', ''),
        'Country': data.get('country_name', ''),
        'Country Code': data.get('country', ''),
        'Latitude': data.get('latitude', ''),
        'Longitude': data.get('longitude', ''),
        'ASN': data.get('asn', ''),
        'ISP': data.get('org', '')
    }

def iplocation(ip):
    url = f"https://api.iplocation.net/?ip={ip}"
    response = requests.get(url)
    data = response.json()
    return {
        'IP': ip,
        'Country': data.get('country_name', ''),
        'City': data.get('city', ''),
        'ISP': data.get('isp', '')
    }

def ipwhois(ip):
    url = f"https://ipwhois.app/json/{ip}"
    response = requests.get(url)
    data = response.json()
    return {
        'IP': ip,
        'Country': data.get('country', ''),
        'Region': data.get('region', ''),
        'City': data.get('city', ''),
        'ASN': data.get('asn', ''),
        'Org': data.get('org', ''),
        'Latitude': data.get('latitude', ''),
        'Longitude': data.get('longitude', '')
    }

def ip_details(ip):
    details = {}
    
    # Collect data from APIs
    details.update(ipinfo(ip))
    details.update(vt_ip(ip))
    details.update(ip2location(ip))
    details.update(db_ip(ip))
    details.update(ipapi(ip))
    details.update(iplocation(ip))
    details.update(ipwhois(ip))

    return details

def save_ip_details(ip, file_name="ip_details.txt"):
    ip_info = ip_details(ip)
    
    # Save to text file
    with open(file_name, "w") as file:
        file.write(f"IP Details for: {ip}\n")
        file.write("="*40 + "\n")
        for key, value in ip_info.items():
            file.write(f"{key}: {value}\n")
        file.write("="*40 + "\n")
    print(f"Details saved in {file_name}")

ip = input("Enter IP Address: ")
save_ip_details(ip)