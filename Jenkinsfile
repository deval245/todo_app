pipeline {
    agent any
    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-cred')
        GITHUB_CREDENTIALS = credentials('github-cred')
        IMAGE_NAME = "devalth/todo-app"
        BRANCH_NAME = "${env.BRANCH_NAME}"
        K8S_NAMESPACE = "todo-app-${env.BRANCH_NAME}"  // Separate namespace per branch (qa, main, develop)
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

        // ✅ Stage 3: Create Namespace if Not Exists
        stage('Create Namespace') {
            steps {
                script {
                    echo "📦 Ensuring Kubernetes namespace '${K8S_NAMESPACE}' exists..."
                    sh """
                        kubectl get namespace ${K8S_NAMESPACE} || kubectl create namespace ${K8S_NAMESPACE}
                    """
                }
            }
        }

        // ✅ Stage 4: Deploy to Kubernetes (Apply Manifests)
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "🚀 Deploying app to Kubernetes in namespace '${K8S_NAMESPACE}'..."

                    // Inject branch name & image dynamically into k8s files before apply
                    sh """
                        # Replace placeholder IMAGE TAG in deployment.yaml dynamically
                        sed 's|IMAGE_PLACEHOLDER|${IMAGE_NAME}:${BRANCH_NAME}|g' k8s/deployment.yaml > k8s/deployment_temp.yaml

                        # Apply Namespace (idempotent)
                        kubectl apply -f k8s/namespace.yaml

                        # Apply Deployment and Service
                        kubectl apply -f k8s/deployment_temp.yaml -n ${K8S_NAMESPACE}
                        kubectl apply -f k8s/service.yaml -n ${K8S_NAMESPACE}
                    """
                }
            }
        }

        // ✅ Stage 5: Health Check for K8s Pod
        stage('Health Check') {
            steps {
                script {
                    echo '🔍 Performing health check for Kubernetes deployment...'
                    sh """
                        sleep 10  # Wait for pods to spin up
                        kubectl get pods -n ${K8S_NAMESPACE}
                        POD_NAME=\$(kubectl get pods -n ${K8S_NAMESPACE} -l app=todo-app -o jsonpath="{.items[0].metadata.name}")
                        kubectl logs \$POD_NAME -n ${K8S_NAMESPACE}
                        kubectl get svc -n ${K8S_NAMESPACE}

                        # Check if Pod is Running
                        kubectl wait --for=condition=ready pod/\$POD_NAME --timeout=60s -n ${K8S_NAMESPACE}
                        echo '✅ App deployed and running successfully on Kubernetes.'
                    """
                }
            }
        }
    }

    // ✅ Post actions for status
    post {
        success {
            echo "🎉 Kubernetes deployment successful on branch: ${BRANCH_NAME}!"
        }
        failure {
            echo "❌ Kubernetes deployment failed on branch: ${BRANCH_NAME}. Check Jenkins logs for more details."
        }
        always {
            echo "📜 Pipeline completed for branch: ${BRANCH_NAME}."
        }
    }
}