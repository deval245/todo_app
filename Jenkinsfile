pipeline {
    agent any

    environment {
        IMAGE_NAME = 'deval245/todo-app'  // ✅ Your DockerHub repo name (replace 'todo-app' with actual repo name on DockerHub if different)
        IMAGE_TAG = 'latest'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git 'https://github.com/deval245/todo_app.git'  // ✅ Your actual GitHub repo
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
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-cred') { // ✅ Your Jenkins DockerHub credentials ID (you'll create this in Jenkins Credentials)
                        docker.image("${IMAGE_NAME}:${IMAGE_TAG}").push()
                    }
                }
            }
        }

        stage('Deploy Application using Docker Compose') {
            steps {
                script {
                    sh 'docker-compose down'  // ✅ Stop existing containers
                    sh 'docker-compose up --build -d'  // ✅ Rebuild and restart containers
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment Successful!"
        }
        failure {
            echo "❌ Pipeline Failed. Please check logs!"
        }
    }
}