pipeline {
    agent any

    environment {
        IMAGE_NAME = 'deval245/todo-app'  // ✅ Your DockerHub repo name
        IMAGE_TAG = 'latest'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/deval245/todo_app.git'  // ✅ Always mention branch
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // ✅ Explicit Dockerfile usage for App (not Jenkins)
                    docker.build("${IMAGE_NAME}:${IMAGE_TAG}", "-f Dockerfile .")
                }
            }
        }

        stage('Push Docker Image to DockerHub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-cred') {  // ✅ Correct credentials ID
                        docker.image("${IMAGE_NAME}:${IMAGE_TAG}").push()  // ✅ Push with tag
                    }
                }
            }
        }

        stage('Deploy Application using Docker Compose') {
            steps {
                script {
                    // ✅ Stop existing containers
                    sh 'docker-compose down'
                    // ✅ Rebuild and deploy latest
                    sh 'docker-compose up --build -d'
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment Successful! Latest image pushed and deployed."
        }
        failure {
            echo "❌ Pipeline Failed. Please check Jenkins logs for errors."
        }
    }
}