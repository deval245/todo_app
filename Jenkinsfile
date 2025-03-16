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
                        echo "⚙️ Stopping running app, Jenkins, and pgAdmin containers if they exist..."

                        # Stop and remove application, Jenkins, and pgAdmin containers (if they exist), but NOT the database container
                        docker rm -f fastapi_todo || true
                        docker rm -f todo_jenkins || true
                        docker rm -f todo_pgadmin || true

                        echo "✅ Cleaned up old app, Jenkins, and pgAdmin containers."

                        echo "🚀 Bringing up all containers with fresh build, preserving database volume..."

                        # Do NOT use --volumes here to preserve PostgreSQL database data
                        docker-compose down --remove-orphans || true

                        docker-compose up --build -d
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