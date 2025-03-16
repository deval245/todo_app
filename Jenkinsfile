pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-cred')
        GITHUB_CREDENTIALS = credentials('github-cred')
        IMAGE_NAME = "devalth/todo-app"
        APP_CONTAINER = "fastapi_todo"
        PGADMIN_CONTAINER = "todo_pgadmin"
        DB_CONTAINER = "todo_postgres"
        BRANCH_NAME = "${env.BRANCH_NAME}"  // Capture branch dynamically
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
                        echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin
                        docker push ${IMAGE_NAME}:${BRANCH_NAME}
                        docker logout
                    """
                }
            }
        }

        stage('Safe Cleanup Old Containers') {
            steps {
                script {
                    echo '⚙️ Cleaning up old containers (except DB)...'
                    sh """
                        docker stop ${APP_CONTAINER} || true && docker rm ${APP_CONTAINER} || true
                        docker stop ${PGADMIN_CONTAINER} || true && docker rm ${PGADMIN_CONTAINER} || true
                    """
                }
            }
        }

        stage('Deploy Environment') {
            steps {
                script {
                    echo "🚀 Deploying using docker-compose.${BRANCH_NAME}.yaml"
                    sh """
                        docker-compose -f docker-compose.${BRANCH_NAME}.yaml pull  # Optional if pulling
                        docker-compose -f docker-compose.${BRANCH_NAME}.yaml up --build -d app pgadmin
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo '🔍 Checking running containers...'
                    sh """
                        docker ps | grep ${APP_CONTAINER} || (echo '❌ App Failed!' && exit 1)
                        docker ps | grep ${PGADMIN_CONTAINER} || (echo '❌ PGAdmin Failed!' && exit 1)
                        echo '✅ All good in ${BRANCH_NAME} environment!'
                    """
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Successful build & deployment on ${BRANCH_NAME}!"
        }
        failure {
            echo "❌ Build or Deployment failed on ${BRANCH_NAME}!"
        }
        always {
            echo "📜 Pipeline finished for ${BRANCH_NAME} (check status)."
        }
    }
}