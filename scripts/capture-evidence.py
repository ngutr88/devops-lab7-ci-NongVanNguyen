"""Capture local Lab 7 service evidence without printing credentials."""
import json
import pathlib
import subprocess
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).resolve().parents[1]
screenshots = root / 'screenshots'
screenshots.mkdir(exist_ok=True)
credentials = json.loads((root / '.private/services.json').read_text(encoding='utf-8'))

def shot(page, name):
    page.screenshot(path=str(screenshots / name), full_page=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1100})

    page.goto('http://localhost:8080/login')
    page.get_by_label('Username').fill('admin')
    page.get_by_label('Password').fill(credentials['jenkinsPassword'])
    page.get_by_role('button', name='Sign in').click()
    page.wait_for_url('**/')
    shot(page, '02-jenkins-dashboard.png')
    page.goto('http://localhost:8080/job/DevOps-Lab7-CI-Pipeline/4/')
    page.wait_for_load_state('domcontentloaded')
    shot(page, '03-pipeline-stage-view.png')
    page.goto('http://localhost:8080/job/DevOps-Lab7-CI-Pipeline/4/console')
    page.wait_for_load_state('domcontentloaded')
    shot(page, '04-console-output.png')
    page.goto('http://localhost:8080/job/DevOps-Lab7-CI-Pipeline/4/testReport/')
    page.wait_for_load_state('domcontentloaded')
    shot(page, '05-test-results.png')
    page.goto('http://localhost:8080/job/DevOps-Lab7-CI-Pipeline/4/artifact/')
    page.wait_for_load_state('domcontentloaded')
    shot(page, '06-artifacts.png')

    nexus_context = browser.new_context(
        viewport={'width': 1440, 'height': 1100},
        http_credentials={'username': 'admin', 'password': credentials['nexusPassword']},
    )
    page = nexus_context.new_page()
    page.goto('http://localhost:8081/service/rest/v1/search/assets?repository=maven-snapshots&group=com.devops.lab7&name=ci-demo')
    shot(page, '07-nexus-artifact.png')

    sonar_context = browser.new_context(
        viewport={'width': 1440, 'height': 1100},
        http_credentials={'username': 'admin', 'password': credentials['sonarPassword']},
    )
    page = sonar_context.new_page()
    page.goto('http://localhost:9000/api/measures/component?component=devops-lab7&metricKeys=bugs,vulnerabilities,code_smells,coverage,ncloc')
    shot(page, '08-sonarqube-dashboard.png')
    browser.close()

docker_ps = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'], check=True, capture_output=True, text=True).stdout
(root / 'evidence' / 'docker-ps.txt').write_text(docker_ps, encoding='utf-8')
print('Browser screenshots and Docker evidence captured.')
