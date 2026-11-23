"""Accept the Nexus Community Edition EULA required before component uploads."""
import base64
import json
import pathlib
import urllib.request

root = pathlib.Path(__file__).resolve().parents[1]
password = json.loads((root / '.private/services.json').read_text(encoding='utf-8'))['nexusPassword']
headers = {
    'Authorization': 'Basic ' + base64.b64encode(f'admin:{password}'.encode()).decode(),
    'Content-Type': 'application/json',
}
endpoint = 'http://localhost:8081/service/rest/v1/system/eula'
with urllib.request.urlopen(urllib.request.Request(endpoint, headers=headers), timeout=30) as response:
    agreement = json.load(response)
if not agreement['accepted']:
    agreement['accepted'] = True
    payload = json.dumps(agreement).encode()
    request = urllib.request.Request(endpoint, data=payload, headers=headers, method='POST')
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 204):
            raise RuntimeError(f'EULA API returned {response.status}')
print('Nexus Community Edition EULA accepted.')
