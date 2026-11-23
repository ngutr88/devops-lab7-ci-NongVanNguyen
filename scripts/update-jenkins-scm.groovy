import hudson.plugins.git.BranchSpec
import hudson.plugins.git.GitSCM
import hudson.plugins.git.UserRemoteConfig
import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import org.jenkinsci.plugins.workflow.job.WorkflowJob

def repositoryUrl = 'https://github.com/ngutr88/devops-lab7-ci-NongVanNguyen.git'
def job = Jenkins.get().getItem('DevOps-Lab7-CI-Pipeline') as WorkflowJob
assert job != null : 'Không tìm thấy Jenkins Job DevOps-Lab7-CI-Pipeline'
def scm = new GitSCM(
    [new UserRemoteConfig(repositoryUrl, null, null, 'github-credentials')],
    [new BranchSpec('*/main')], false, [], null, null, []
)
job.setDefinition(new CpsScmFlowDefinition(scm, 'sample-java-app/Jenkinsfile'))
job.save()
Jenkins.get().save()
println("Jenkins Job đã đổi repository sang: ${repositoryUrl}")
