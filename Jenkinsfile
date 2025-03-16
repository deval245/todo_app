pipeline {
    agent any

    environment {
        IMAGE_NAME = 'devalth/todo-app'
        IMAGE_TAG = 'latest'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git credentialsId: 'github-cred', url: 'https://github.com/deval245/todo_app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }

        stage('Push Docker Image to DockerHub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-cred') {
                        docker.image("${IMAGE_NAME}:${IMAGE_TAG}").push()
                    }
                }
            }
        }

        stage('Clean and Deploy Containers (Without Dropping DB)') {
            steps {
                script {
                    sh '''
                        echo "⚙️ Stopping running app and pgAdmin containers if they exist..."
                        docker rm -f fastapi_todo || true
                        docker rm -f todo_pgadmin || true
                        echo "✅ Cleaned up old app and pgAdmin containers."

                        echo "🚀 Bringing up app and pgAdmin fresh, preserving DB..."
                        docker-compose up --build -d app pgadmin
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment Successful!"
        }
        failure {
            echo "❌ Pipeline Failed. Please check Jenkins logs for errors."
        }
    }
}