pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-cred')  // DockerHub credential ID
        GITHUB_CREDENTIALS = credentials('github-cred')        // GitHub credential ID
        IMAGE_NAME = "devalth/todo-app"
        APP_CONTAINER = "fastapi_todo"
        PGADMIN_CONTAINER = "todo_pgadmin"
        DB_CONTAINER = "todo_postgres"
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo '🧾 Checking out code from GitHub...'
                git branch: 'main', credentialsId: "${env.GITHUB_CREDENTIALS}", url: 'https://github.com/deval245/todo_app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo '🐳 Building the Docker image...'
                    sh "docker build -t ${IMAGE_NAME}:latest ."
                }
            }
        }

        stage('Push Docker Image to DockerHub') {
            steps {
                script {
                    echo '🔐 Logging into DockerHub and pushing image...'
                    sh """
                    echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin
                    docker tag ${IMAGE_NAME}:latest index.docker.io/${IMAGE_NAME}:latest
                    docker push index.docker.io/${IMAGE_NAME}:latest
                    docker logout
                    """
                }
            }
        }

        stage('Clean and Prepare Containers (Safe for DB)') {
            steps {
                script {
                    echo '⚙️ Stopping and removing old containers except for DB...'
                    sh """
                    # Handle App container
                    if [ \$(docker ps -q -f name=${APP_CONTAINER}) ]; then
                        echo '🛑 Stopping App container...'
                        docker stop ${APP_CONTAINER}
                        docker rm ${APP_CONTAINER}
                    fi

                    # Handle PGAdmin container
                    if [ \$(docker ps -q -f name=${PGADMIN_CONTAINER}) ]; then
                        echo '🛑 Stopping PGAdmin container...'
                        docker stop ${PGADMIN_CONTAINER}
                        docker rm ${PGADMIN_CONTAINER}
                    fi

                    # Handle DB container (Don't touch for safety)
                    if [ \$(docker ps -q -f name=${DB_CONTAINER}) ]; then
                        echo '✅ DB is running safely and will be reused!'
                    else
                        echo '⚠️ WARNING: DB is NOT running. Please check manually!'
                    fi
                    """
                }
            }
        }

        stage('Deploy Fresh App and PGAdmin (Preserve DB)') {
            steps {
                script {
                    echo '🚀 Bringing up App and PGAdmin, DB preserved!'
                    sh """
                    docker-compose up --build -d app pgadmin
                    """
                }
            }
        }

        stage('Post-Deployment Health Check') {
            steps {
                script {
                    echo '🔍 Running Health Checks for App and PGAdmin...'
                    sh """
                    if [ ! \$(docker ps -q -f name=${APP_CONTAINER}) ]; then
                        echo '❌ ERROR: App container failed to start.'
                        exit 1
                    fi

                    if [ ! \$(docker ps -q -f name=${PGADMIN_CONTAINER}) ]; then
                        echo '❌ ERROR: PGAdmin container failed to start.'
                        exit 1
                    fi

                    echo '✅ Both App and PGAdmin are up and running successfully.'
                    """
                }
            }
        }
    }

    post {
        success {
            echo '🎉 Deployment successful and running smoothly!'
        }
        failure {
            echo '❌ Deployment failed! Check the above logs to debug.'
            // 🔔 Optional: Add Slack/Email notification for failures here
        }
        always {
            echo '📜 Pipeline finished (check status above).'
        }
    }
}