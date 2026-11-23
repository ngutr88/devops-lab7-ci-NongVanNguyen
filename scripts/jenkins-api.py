"""Authenticated local Jenkins API helper; avoids printing credentials."""
import base64
import http.cookiejar
import json
import pathlib
import sys
import urllib.parse
import urllib.request

root = pathlib.Path(__file__).resolve().parents[1]
values = json.loads((root / '.private/services.json').read_text())
auth = 'Basic ' + base64.b64encode(('admin:' + values['jenkinsPassword']).encode()).decode()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
opener.addheaders = [('Authorization', auth)]
base = 'http://localhost:8080/'
mode, path = sys.argv[1:3]
if mode == 'get':
    with opener.open(base + path, timeout=60) as response:
        sys.stdout.buffer.write(response.read())
else:
    crumb = json.load(opener.open(base + 'crumbIssuer/api/json'))
    headers = {crumb['crumbRequestField']: crumb['crumb']}
    payload = b''
    if mode == 'script':
        payload = urllib.parse.urlencode({'script': pathlib.Path(path).read_text(encoding='utf-8')}).encode()
        path = 'scriptText'
    req = urllib.request.Request(base + path, data=payload, headers=headers, method='POST')
    with opener.open(req, timeout=120) as response:
        sys.stdout.buffer.write(response.read())
