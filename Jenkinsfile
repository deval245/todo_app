pipeline {
    agent any
    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-cred')
        GITHUB_CREDENTIALS = credentials('github-cred')
        IMAGE_NAME = "devalth/todo-app"
        BRANCH_NAME = "${env.BRANCH_NAME}"
        APP_CONTAINER = "fastapi_todo_${env.BRANCH_NAME}"
        DOCKER_COMPOSE_FILE = "docker-compose.${env.BRANCH_NAME}.yaml"
    }

    stages {

        // ✅ Stage 1: Checkout Code
        stage('Checkout Code') {
            steps {
                echo "🧾 Checking out branch: ${BRANCH_NAME}"
                git branch: "${BRANCH_NAME}", credentialsId: "${GITHUB_CREDENTIALS}", url: 'https://github.com/deval245/todo_app.git'
            }
        }

        // ✅ Stage 2: Build & Push Docker Image
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

        // ✅ Stage 3: Ensure Network Exists
        stage('Ensure Network Exists') {
            steps {
                echo "🌐 Ensuring network 'todo_network' exists..."
                sh "docker network inspect todo_network >/dev/null 2>&1 || docker network create todo_network"
            }
        }

        // ✅ Stage 4: Stop & Remove Previous Container (if running)
        stage('Stop & Remove Old Container') {
            steps {
                script {
                    echo "🧹 Stopping & removing old container if exists: ${APP_CONTAINER}"
                    sh """
                        docker ps -a --format '{{.Names}}' | grep -w ${APP_CONTAINER} && docker rm -f ${APP_CONTAINER} || echo 'ℹ️ No existing container to remove.'
                    """
                }
            }
        }

        // ✅ Stage 5: Deploy App Container (Pull & Up)
        stage('Deploy App Container') {
            steps {
                script {
                    echo "🚀 Deploying app container for branch: ${BRANCH_NAME} using ${DOCKER_COMPOSE_FILE}"
                    sh """
                        docker-compose -f ${DOCKER_COMPOSE_FILE} pull
                        docker-compose -f ${DOCKER_COMPOSE_FILE} down --remove-orphans
                        docker-compose -f ${DOCKER_COMPOSE_FILE} up --build --force-recreate -d
                    """
                }
            }
        }

        // ✅ Stage 6: Health Check to ensure container is up
        stage('Health Check') {
            steps {
                script {
                    echo '🔍 Performing health check for app container...'
                    sh """
                        sleep 10  # Wait for the container to be ready
                        docker ps | grep ${APP_CONTAINER} || (echo '❌ App container is not running!' && exit 1)
                        echo '✅ App container is running successfully.'
                    """
                }
            }
        }
    }

    // ✅ Post actions for status
    post {
        success {
            echo "🎉 Deployment successful on branch: ${BRANCH_NAME}!"
        }
        failure {
            echo "❌ Deployment failed on branch: ${BRANCH_NAME}. Check Jenkins logs for more details."
        }
        always {
            echo "📜 Pipeline completed for branch: ${BRANCH_NAME}."
        }
    }
}