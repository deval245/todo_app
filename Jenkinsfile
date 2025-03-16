pipeline {
    agent any
    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-cred')
        GITHUB_CREDENTIALS = credentials('github-cred')
        IMAGE_NAME = "devalth/todo-app"
        BRANCH_NAME = "${env.BRANCH_NAME}"
        APP_CONTAINER = "fastapi_todo_${env.BRANCH_NAME}"
    }
    stages {
        stage('Checkout Code') {
            steps {
                echo "🧾 Checking out branch: ${env.BRANCH_NAME}"
                git branch: "${env.BRANCH_NAME}", credentialsId: "${env.GITHUB_CREDENTIALS}", url: 'https://github.com/deval245/todo_app.git'
            }
        }

        stage('Build & Push Docker Image') {
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

        stage('Ensure Network Exists') {
            steps {
                echo "🌐 Ensuring network 'todo_network' exists..."
                sh "docker network inspect todo_network >/dev/null 2>&1 || docker network create todo_network"
            }
        }

        stage('Deploy App Container') {
            steps {
                script {
                    echo "🚀 Deploying app container for branch: ${BRANCH_NAME}"
                    sh """
                        docker-compose -f docker-compose.${BRANCH_NAME}.yaml pull
                        docker-compose -f docker-compose.${BRANCH_NAME}.yaml up --build --force-recreate -d
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo '🔍 Checking if app is running...'
                    sh """
                        docker ps | grep ${APP_CONTAINER} || (echo '❌ App container is not running!' && exit 1)
                        echo '✅ App container is running.'
                    """
                }
            }
        }
    }
    post {
        success { echo "🎉 Deployment successful on ${BRANCH_NAME}!" }
        failure { echo "❌ Deployment failed on ${BRANCH_NAME}. Check Jenkins logs." }
        always  { echo "📜 Pipeline completed for branch: ${BRANCH_NAME}." }
    }
}