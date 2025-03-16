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

        stage('Checkout Code') {
            steps {
                echo "🧾 Checking out branch: ${env.BRANCH_NAME}"
                git branch: "${env.BRANCH_NAME}", credentialsId: "${env.GITHUB_CREDENTIALS}", url: 'https://github.com/deval245/todo_app.git'
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    echo '🐳 Building & pushing image to DockerHub...'
                    sh """
                        docker build -t ${IMAGE_NAME}:${BRANCH_NAME} .
                        echo '${DOCKERHUB_CREDENTIALS_PSW}' | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin
                        docker push ${IMAGE_NAME}:${BRANCH_NAME}
                        docker logout
                    """
                }
            }
        }

        stage('Approval for QA & Main') {
            when {
                branch 'qa'
                branch 'main'
            }
            steps {
                input message: "Approve deployment to ${env.BRANCH_NAME}?"
            }
        }

        stage('Deploy Environment') {
            steps {
                script {
                    echo "🚀 Deploying using docker-compose.${BRANCH_NAME}.yaml"
                    sh """
                        docker-compose -f docker-compose.${BRANCH_NAME}.yaml pull || echo 'Skipping pull, using local images...'
                        docker-compose -f docker-compose.${BRANCH_NAME}.yaml up --build -d app pgadmin
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo '🔍 Performing health checks...'
                    sh """
                        docker ps | grep ${APP_CONTAINER} || (echo '❌ App container down!' && exit 1)
                        docker ps | grep ${PGADMIN_CONTAINER} || (echo '❌ PGAdmin container down!' && exit 1)
                        echo '✅ Deployment healthy!'
                    """
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Deployment successful on ${BRANCH_NAME}!"
        }
        failure {
            echo "❌ Deployment failed on ${BRANCH_NAME}. Check logs!"
        }
        always {
            echo "📜 Pipeline execution finished for ${BRANCH_NAME}."
        }
    }
}