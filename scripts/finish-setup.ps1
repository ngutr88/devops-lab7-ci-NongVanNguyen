$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
function Docker-Checked {
    & docker @args
    if ($LASTEXITCODE -ne 0) { throw "Docker operation failed: $($args[0])" }
}
function Wait-Http($Url, $DeadlineSeconds = 600) {
    $deadline = (Get-Date).AddSeconds($DeadlineSeconds)
    do {
        try {
            $r = Invoke-WebRequest -UseBasicParsing $Url -TimeoutSec 5
            if ($r.StatusCode -eq 200) { return }
        } catch { }
        Start-Sleep -Seconds 5
    } while ((Get-Date) -lt $deadline)
    throw "Service did not become ready: $Url"
}
Docker-Checked compose up -d
Wait-Http 'http://localhost:8081/service/rest/v1/status'
Wait-Http 'http://localhost:9000/api/system/status'
$deadline = (Get-Date).AddMinutes(10)
while ((Invoke-RestMethod 'http://localhost:9000/api/system/status').status -ne 'UP') {
    if ((Get-Date) -gt $deadline) { throw 'SonarQube startup timed out' }
    Start-Sleep -Seconds 5
}
python scripts/configure-services.py
if ($LASTEXITCODE -ne 0) { throw 'Service configuration failed' }
Docker-Checked cp scripts/plugins.txt lab7-jenkins:/tmp/lab7-plugins.txt
Docker-Checked exec lab7-jenkins jenkins-plugin-cli --plugin-file /tmp/lab7-plugins.txt --plugin-download-directory /var/jenkins_home/plugins
Docker-Checked cp .tools/apache-maven-3.9.9 lab7-jenkins:/opt/maven
Docker-Checked exec -u root lab7-jenkins chmod +x /opt/maven/bin/mvn
Docker-Checked cp .private/services.json lab7-jenkins:/var/jenkins_home/lab7-secrets.json
Docker-Checked cp config/maven-settings-nexus.xml lab7-jenkins:/var/jenkins_home/lab7-maven-settings.xml
Docker-Checked exec lab7-jenkins mkdir -p /var/jenkins_home/init.groovy.d
Docker-Checked cp scripts/bootstrap.groovy lab7-jenkins:/var/jenkins_home/init.groovy.d/lab7.groovy
Docker-Checked restart lab7-jenkins
Wait-Http 'http://localhost:8080/login' 600
Start-Sleep -Seconds 10
python scripts/jenkins-api.py get api/json
if ($LASTEXITCODE -ne 0) { throw 'Jenkins configuration failed; inspect container logs' }
# Remove the one-time bootstrap and plaintext secret copies after successful setup.
Docker-Checked exec lab7-jenkins rm /var/jenkins_home/init.groovy.d/lab7.groovy /var/jenkins_home/lab7-secrets.json
python scripts/jenkins-api.py post job/DevOps-Lab7-CI-Pipeline/build
if ($LASTEXITCODE -ne 0) { throw 'Could not start pipeline' }
Write-Output 'Pipeline triggered. Inspect http://localhost:8080/job/DevOps-Lab7-CI-Pipeline/'
