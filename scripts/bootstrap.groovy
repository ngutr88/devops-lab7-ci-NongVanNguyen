import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import jenkins.install.InstallState
import com.cloudbees.plugins.credentials.CredentialsScope
import com.cloudbees.plugins.credentials.SystemCredentialsProvider
import com.cloudbees.plugins.credentials.domains.Domain
import com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl
import org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl
import hudson.util.Secret
import hudson.tasks.Maven
import hudson.plugins.sonar.SonarInstallation
import hudson.plugins.sonar.SonarGlobalConfiguration
import org.jenkinsci.plugins.configfiles.GlobalConfigFiles
import org.jenkinsci.plugins.configfiles.maven.MavenSettingsConfig
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import hudson.plugins.git.GitSCM
import hudson.plugins.git.UserRemoteConfig
import hudson.plugins.git.BranchSpec

// Run once after installing plugins. Secrets are copied separately, never committed.
def j = Jenkins.get()
def secrets = new groovy.json.JsonSlurper().parse(new File('/var/jenkins_home/lab7-secrets.json'))
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount('admin', secrets.jenkinsPassword)
j.setSecurityRealm(realm)
def authorization = new FullControlOnceLoggedInAuthorizationStrategy()
authorization.setAllowAnonymousRead(false)
j.setAuthorizationStrategy(authorization)
j.setNumExecutors(1)
j.setInstallState(InstallState.INITIAL_SETUP_COMPLETED)
def store = SystemCredentialsProvider.getInstance().getStore()
store.addCredentials(Domain.global(), new UsernamePasswordCredentialsImpl(CredentialsScope.GLOBAL, 'github-credentials', 'Lab 7 private GitHub checkout', secrets.githubUser, secrets.githubToken))
store.addCredentials(Domain.global(), new UsernamePasswordCredentialsImpl(CredentialsScope.GLOBAL, 'nexus-credentials', 'Lab 7 Nexus', 'admin', secrets.nexusPassword))
store.addCredentials(Domain.global(), new StringCredentialsImpl(CredentialsScope.GLOBAL, 'sonarqube-token', 'Lab 7 SonarQube', Secret.fromString(secrets.sonarToken)))
j.getDescriptorByType(Maven.DescriptorImpl.class).setInstallations(new Maven.MavenInstallation('M3', '/opt/maven', []))
def sonar = j.getDescriptorByType(SonarGlobalConfiguration.class)
sonar.setInstallations(new SonarInstallation('SonarQube', 'http://lab7-sonarqube:9000', 'sonarqube-token', null, null, null, null, null, null))
sonar.save()
def settings = new File('/var/jenkins_home/lab7-maven-settings.xml').text
GlobalConfigFiles.get().save(new MavenSettingsConfig('maven-settings-nexus', 'Lab7 Nexus settings', 'Environment-bound credentials', settings, false, []))
def job = j.getItem('DevOps-Lab7-CI-Pipeline') ?: j.createProject(WorkflowJob.class, 'DevOps-Lab7-CI-Pipeline')
def scm = new GitSCM([new UserRemoteConfig('https://github.com/' + secrets.githubUser + '/devops-lab7-ci-demo.git', null, null, 'github-credentials')], [new BranchSpec('*/main')], false, [], null, null, [])
job.setDefinition(new CpsScmFlowDefinition(scm, 'sample-java-app/Jenkinsfile'))
job.save()
jenkins.model.JenkinsLocationConfiguration.get().setUrl('http://localhost:8080/')
j.save()
println('LAB7_BOOTSTRAP_COMPLETE')
