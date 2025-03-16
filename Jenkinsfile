pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-cred')
        GITHUB_CREDENTIALS = credentials('github-cred')
        IMAGE_NAME = "devalth/todo-app"
        APP_CONTAINER = "fastapi_todo"
        PGADMIN_CONTAINER = "todo_pgadmin"
        BRANCH_NAME = "${env.BRANCH_NAME}"
    }

    stages {

        // 1. Checkout Stage
        stage('Checkout Code') {
            steps {
                echo "🧾 Checking out branch: ${env.BRANCH_NAME}"
                git branch: "${env.BRANCH_NAME}", credentialsId: "${env.GITHUB_CREDENTIALS}", url: 'https://github.com/deval245/todo_app.git'
            }
        }

        // 2. Build & Push Docker Image (only for deployable branches)
        stage('Build & Push Docker Image') {
            when {
                anyOf {
                    branch 'develop'
                    branch 'qa'
                    branch 'main'
                }
            }
            steps {
                script {
                    echo '🐳 Building & pushing Docker image to DockerHub...'
                    sh """
                        docker build -t ${IMAGE_NAME}:${BRANCH_NAME} .
                        echo '${DOCKERHUB_CREDENTIALS_PSW}' | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin
                        docker push ${IMAGE_NAME}:${BRANCH_NAME}
                        docker logout
                    """
                }
            }
        }

        // 3. Approval (for QA & Main)
        stage('Approval for QA & Main') {
            when {
                anyOf {
                    branch 'qa'
                    branch 'main'
                }
            }
            steps {
                input message: "Approve deployment to ${env.BRANCH_NAME}?"
            }
        }

        // 4. Deploy Environment
        stage('Deploy Environment') {
            steps {
                script {
                    // Default compose file for branches like 'feature-*' or 'others'
                    def composeFile = 'docker-compose.yaml'

                    // Dynamically pick correct YAML based on branch name
                    if (BRANCH_NAME == 'develop') {
                        composeFile = 'docker-compose.develop.yaml'
                    } else if (BRANCH_NAME == 'qa') {
                        composeFile = 'docker-compose.qa.yaml'
                    } else if (BRANCH_NAME == 'main') {
                        composeFile = 'docker-compose.main.yaml'
                    }

                    echo "🚀 Deploying using: ${composeFile}"

                    // Stop previous containers if any, and deploy new
                    sh """
                        docker-compose -f ${composeFile} down || echo 'Nothing to stop, fresh start.'
                        docker-compose -f ${composeFile} pull || echo 'Using local image, no pull needed.'
                        docker-compose -f ${composeFile} up --build -d
                    """
                }
            }
        }

        // 5. Health Check
        stage('Health Check') {
            steps {
                script {
                    echo '🔍 Running health checks...'
                    sh """
                        docker ps | grep ${APP_CONTAINER} || (echo '❌ App container not running!' && exit 1)
                        docker ps | grep ${PGADMIN_CONTAINER} || (echo '❌ PGAdmin container not running!' && exit 1)
                        echo '✅ All containers are running properly!'
                    """
                }
            }
        }
    }

    // 6. Post Build Handling
    post {
        success {
            echo "🎉 Deployment successful on branch: ${BRANCH_NAME}!"
        }
        failure {
            echo "❌ Deployment failed on branch: ${BRANCH_NAME}. Please check Jenkins logs."
        }
        always {
            echo "📜 Pipeline completed for branch: ${BRANCH_NAME}."
        }
    }
}