import requests
import os
import json

API_KEY = os.environ.get('API_KEY')
API_KEY_NAME = os.environ.get('API_KEY_NAME')

def main():
    url = f"{os.environ.get('API_URL')}/product"
    headers = {
        f"{API_KEY_NAME}": f"{API_KEY}",
        "Content-Type": "application/json"
    }

    # Load query files from 'json' folder
    data_folder = '/json/'
    requests_json = []
    if os.path.exists(data_folder) and os.path.isdir(data_folder):
        for file_name in os.listdir(data_folder):
            if file_name.endswith('.json'):
                file_path = os.path.join(data_folder, file_name)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    requests_json.append(data)

    for tab_request in requests_json:
        for query in tab_request:
            try:
                response = requests.post(url, headers=headers, json=query)
            except Exception as e:
                print("Error API Ecobalyse:", e)
            else:
                if response.status_code == 200:
                    print(response.json())

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        sys.stdout.write('[+] Exit requested')