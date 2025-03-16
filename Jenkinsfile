pipeline {
    agent any

    environment {
        IMAGE_NAME = 'devalth/todo-app'
        IMAGE_TAG = 'latest'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git credentialsId: 'aa1e19cf-82e1-4a8a-9200-d15c06f4c0dd', url: 'https://github.com/deval245/todo_app.git'
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
                    docker.withRegistry('https://index.docker.io/v1/', 'e4c0f518-e388-4d8b-9402-c1fe4d33cc44') {
                        docker.image("${IMAGE_NAME}:${IMAGE_TAG}").push()
                    }
                }
            }
        }

        stage('Deploy Application using Docker Compose') {
            steps {
                script {
                    // ✅ First forcefully remove any conflicting containers dynamically
                    sh '''
                        for container in todo_postgres todo_pgadmin fastapi_todo; do
                            if [ $(docker ps -a -q -f name=$container) ]; then
                                echo "⚙️ Removing old container: $container ..."
                                docker rm -f $container
                            fi
                        done
                    '''

                    // ✅ Bring down existing setup if any (with volumes and orphans cleanup)
                    sh 'docker-compose down --volumes --remove-orphans || true'

                    // ✅ Rebuild and start everything freshly
                    sh 'docker-compose up --build -d'
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