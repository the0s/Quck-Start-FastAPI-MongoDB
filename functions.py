import requests

def get_tfl_data(lines: str):
    r = requests.get(f'https://api.tfl.gov.uk/Line/{lines}/Disruption')
    if r.status_code == 200:
        return r.json()
    else:
        return None

