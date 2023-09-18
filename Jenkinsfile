library identifier: 'jenkins-libs@master', retriever: modernSCM(
  [$class: 'GitSCMSource',
   remote: 'https://github.com/pagaya/jenkins.git',
   credentialsId: 'github-devops-services'])

def parallelStages = [:]

DEV_ACCOUNT_NUMBER = '039139996217'
TESTS_REPORTS_PATH = './junitxml_report.xml'

pipeline {
    agent {
        kubernetes {
            defaultContainer 'builder'
            yamlFile '.infra/jenkins-slave.yaml'
        }
    }
    options {
        timeout(time: 3, unit: 'HOURS')
        ansiColor('xterm')
    }

    parameters {
        booleanParam(name: 'FORCE_DEVELOPMENT_DEPLOY', defaultValue: false, description: 'force deploy to development environment')
        booleanParam(name: 'BUILD_DOCKER_IMAGE', defaultValue: false, description: 'Build Docker image')
    }
    environment {
        PYPI_CRED = credentials('pypi-user-pass')
        AWS_DEFAULT_REGION = 'us-east-1'
        CICD_ACCOUNT_NUMBER = '704102000649'
        CICD_ACCOUNT_ROLE = 'JenkinsCrossAccountRole'
        ECR_REPO_URL = 'dkr.ecr.us-east-1.amazonaws.com'
        REPOSITORY = '704102000649.dkr.ecr.us-east-1.amazonaws.com/via'
        REPO_NAME = 'via'
        GH_TOKEN = credentials('jenkins-eng-github-token')
        GIT_HASH = "${GIT_COMMIT[0..7]}"
        SNYK_TOKEN = credentials('snyk-token')
        APP_WORKDIR   = "services/via-app/"
        CODE_ARTIFCAT_REPO_URL = "https://pagaya-artifacts-704102000649.d.codeartifact.${AWS_DEFAULT_REGION}.amazonaws.com/pypi/Pagaya-Artifacts-prod/"
        CODE_ARTIFACT_AUTH_TOKEN = ""
    }
    stages {
        stage('Get CodeArtifact Token') {
            steps {
                script {
                    withAWS(roleAccount: DEV_ACCOUNT_NUMBER, role: CICD_ACCOUNT_ROLE) {
                        CODE_ARTIFACT_AUTH_TOKEN = sh(
                            returnStdout: true,
                            script: 'aws codeartifact get-authorization-token \
                            --domain pagaya-artifacts \
                            --domain-owner 704102000649 \
                            --region ${AWS_DEFAULT_REGION} \
                            --query authorizationToken \
                            --output text'
                        ).trim()

                        PDM_PYPI_URL = "https://aws:$CODE_ARTIFACT_AUTH_TOKEN@pagaya-artifacts-704102000649.d.codeartifact.${AWS_DEFAULT_REGION}.amazonaws.com/pypi/Pagaya-Artifacts-prod/simple/"
                    }
                }
            }
        }

        stage('publish via-canonical package') {
            when {
                allOf {
                    branch "development"
                    changeset "libs/via-canonical/src/via_canonical_actions/_version.py"
                }
            }
            steps {
               publish_package_to_code_artifact("libs/via-canonical")
            }
        }


        stage('Docker Build & Push') {
            when {
                anyOf {
                    environment name: 'BUILD_DOCKER_IMAGE', value: 'true'
                    branch "development"
                }
            }
            steps {
                script{
                     BRANCH_NORMALIZE = env.BRANCH_NAME.replace("/", "-")
                    if (env.BRANCH_NAME.contains("release")){
                        docker_tags = "${REPOSITORY}:${GIT_COMMIT[0..7]} -t ${REPOSITORY}:release_candidate -t ${REPOSITORY}:${BRANCH_NORMALIZE}"
                    }
                    else{
                        docker_tags = "${REPOSITORY}:${GIT_COMMIT[0..7]}"
                    }
                    }
                    sh """
                    echo "DOCKER TGAS ${docker_tags}"
                        aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${CICD_ACCOUNT_NUMBER}.${ECR_REPO_URL}
                        docker build \
                        -t ${docker_tags} \
                        --build-arg=PDM_PYPI_URL=${PDM_PYPI_URL} \
                        --build-arg=COMMIT_HASH=${GIT_COMMIT[0..7]} ${APP_WORKDIR}
                        docker push ${REPOSITORY} --all-tags
                    """
            }
        }

        stage('Tests') {
            steps {
                tests("services/via-app")
            }
        }
        stage('Develoment Deployment') {
            when {
                anyOf {
                    allOf{
                       environment name: 'BUILD_DOCKER_IMAGE', value: 'true'
                       environment name: 'FORCE_DEVELOPMENT_DEPLOY', value: 'true'
                    }
                    branch "development"
                }
            }
            environment {
                  ENVIRONMENT = "development"
                }
            steps {
                update_environment_image_tag()
        }
    }
}
post {
    always {
        publishHTML(target : [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'unit-test-report',
                reportFiles: 'index.html',
                reportName: 'Unit Test Report',
                reportTitles: 'Via Unit Test Report'])
            publishHTML(target : [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'pytest-report',
                reportFiles: 'index.html',
                reportName: 'Pytest Report',
                reportTitles: 'Via Pytest Report'])
    }
}
}

def update_environment_image_tag(){
    dir ("${REPO_NAME}-infra"){
        git credentialsId: 'jenkins-eng-github-token', url: 'https://github.com/pagaya/via-infra.git'
        sh """
            yq e -i '.via.image.tag = "${GIT_COMMIT[0..7]}"' helm/${REPO_NAME}/values-${ENVIRONMENT}.yaml
            cat helm/${REPO_NAME}/values-${ENVIRONMENT}.yaml
            git config --global url.'https://${GH_TOKEN}@github.com'.insteadOf https://github.com
            git config --global --add safe.directory ${WORKSPACE}/${REPO_NAME}-infra
            git config --global user.email "devops-services@pagaya.com"
            git config --global user.name "Jenkins"
            git commit -am "update ${ENVIRONMENT} image tag to ${GIT_COMMIT[0..7]}"
            git push origin master
        """
    }
}

def publish_package_to_code_artifact(package_path){
    container("python3"){
        dir("${package_path}") {
            sh """
                export PDM_PYPI_URL=$PDM_PYPI_URL
                pip3 install --upgrade pip && pip3 install pdm
                pdm install -L pdm.standalone.lock
                pdm run checks:junit ${WORKSPACE}/publish-package-report
                pdm publish --repository ${CODE_ARTIFCAT_REPO_URL} --username aws --password ${CODE_ARTIFACT_AUTH_TOKEN}
            """
        }
    }
}

def tests(app_path){
    dir("${app_path}"){
        container("python3"){
            sh """
                yum groupinstall -y 'Development Tools'
                yum install -y libxslt-devel libxml2-devel
                export PDM_PYPI_URL=$PDM_PYPI_URL
                pip3 install pdm
                pdm install -L pdm.standalone.lock
                pdm run checks:junit ${WORKSPACE}/unit-test-report
            """
    }
    }
}
