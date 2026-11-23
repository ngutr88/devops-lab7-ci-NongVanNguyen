"""Configure fresh Lab 7 services. Secrets stay in ignored .private/ directory."""
import base64
import json
import pathlib
import secrets
import subprocess
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.private'
PRIVATE.mkdir(exist_ok=True)

def request(url, user, password, data=None, method=None, content_type=None):
    headers = {'Authorization': 'Basic ' + base64.b64encode(f'{user}:{password}'.encode()).decode()}
    if isinstance(data, dict):
        data = urllib.parse.urlencode(data).encode()
        content_type = 'application/x-www-form-urlencoded'
    elif isinstance(data, str):
        data = data.encode()
    if content_type:
        headers['Content-Type'] = content_type
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as response:
        raw = response.read()
        return json.loads(raw) if raw else None

path = PRIVATE / 'services.json'
if path.exists():
    raise SystemExit('Configuration already exists; refusing to reset service credentials.')
values = {key: secrets.token_urlsafe(24) for key in ('jenkinsPassword', 'nexusPassword', 'sonarPassword')}
credential = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True, check=True).stdout
credential = dict(line.split('=', 1) for line in credential.splitlines() if '=' in line)
values.update(githubUser='ngutr88', githubToken=credential['password'])
# Persist before mutations so partial failures are recoverable.
path.write_text(json.dumps(values), encoding='utf-8')
nexus_initial = subprocess.check_output(['docker', 'exec', 'lab7-nexus', 'cat', '/nexus-data/admin.password'], text=True).strip()
request('http://localhost:8081/service/rest/v1/security/users/admin/change-password', 'admin', nexus_initial, values['nexusPassword'], 'PUT', 'text/plain')
eula = request('http://localhost:8081/service/rest/v1/system/eula', 'admin', values['nexusPassword'])
if not eula['accepted']:
    eula['accepted'] = True
    request('http://localhost:8081/service/rest/v1/system/eula', 'admin', values['nexusPassword'], json.dumps(eula), 'POST', 'application/json')
request('http://localhost:8081/service/rest/v1/security/anonymous', 'admin', values['nexusPassword'], json.dumps({'enabled': True, 'userId': 'anonymous', 'realmName': 'NexusAuthorizingRealm'}), 'PUT', 'application/json')
repositories = request('http://localhost:8081/service/rest/v1/repositories', 'admin', values['nexusPassword'])
assert any(r['name'] == 'maven-snapshots' for r in repositories), 'maven-snapshots repository missing'
request('http://localhost:9000/api/users/change_password', 'admin', 'admin', {'login': 'admin', 'previousPassword': 'admin', 'password': values['sonarPassword']})
values['sonarToken'] = request('http://localhost:9000/api/user_tokens/generate', 'admin', values['sonarPassword'], {'name': 'lab7-jenkins'})['token']
path.write_text(json.dumps(values), encoding='utf-8')
print('Nexus and SonarQube configured; secrets saved locally (not printed).')
