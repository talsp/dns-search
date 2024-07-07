import requests
#import dns.resolver
import pandas as pd
from datetime import datetime
from requests.adapters import HTTPAdapter


def check_expiry(date_string):
    try:
        date_object = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S') 
        
        now = datetime.now()
        
        if date_object < now:
            return True
        else:
            return False
    except Exception as e:
        print("[-] Expiry check error")
        print(e)

def get_status_code(url):
    try:
        session = requests.Session()

        retries = 0
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = session.get(f'https://{url}', timeout=5)

        return response.status_code
    except Exception as e:
        print("[-] Error with fetching response code")
        print(e)


def find_subdomains(domain):
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    try:
        response = requests.get(url)
        json_data = response.json()
        #subdomains = set()
        subdomains = []
        for entry in json_data:
            print(f"[+] fetching data for {entry['name_value']}")
            expired = check_expiry(entry['not_after'])
            status_code = get_status_code(entry['name_value'])
            data = {'name': entry['name_value'], "expiry_date": entry['not_after'], "issuer_name": entry['issuer_name'], "expired": expired, "status_code": status_code}
            subdomains.append(data)
        return subdomains
    except Exception as e:
        print(f"Error fetching subdomains from crt.sh: {e}")
        return set()

   

if __name__ == "__main__":
    domain = input("[+] Please Enter the domain: ")
    print("[+] Searching subdomains")

    subdomains = find_subdomains(domain)
    
    print("[+] Subdomains found:")

    unique_names = set()
    for item in subdomains:
        names = item['name'].split('\n')
        for name in names:
            unique_names.add((name, item['expiry_date']))

    df = pd.DataFrame(subdomains)
    df_unique = df.drop_duplicates(subset=['name'])
    print(df_unique)

    output_file = f'output-{domain}.xlsx'
    df_unique.to_excel(output_file, index=False)

    print(f"[+] DataFrame has been exported to {output_file}")



    #for name, expiry_date in unique_names:
     #   print(f"Name: {name}, Expiry Date: {expiry_date}")
