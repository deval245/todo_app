pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-cred')
        GITHUB_CREDENTIALS = credentials('github-cred')
        IMAGE_NAME = "devalth/todo-app"
        BRANCH_NAME = "${env.BRANCH_NAME}"
        K8S_NAMESPACE = "todo-app-${env.BRANCH_NAME}"  // Per branch namespace (qa, dev, main)
        KUBECONFIG = "/root/.kube/config" // ✅ Point to Kubernetes Docker Desktop config
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
                    echo '🐳 Building and pushing Docker image to DockerHub...'
                    withCredentials([usernamePassword(credentialsId: 'docker-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            docker build -t ${IMAGE_NAME}:${BRANCH_NAME} .
                            echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                            docker push ${IMAGE_NAME}:${BRANCH_NAME}
                            docker logout
                        """
                    }
                }
            }
        }

        // ✅ Stage 3: Create Kubernetes Namespace (If not exists)
        stage('Create Namespace') {
            steps {
                script {
                    echo "📦 Creating or ensuring Kubernetes namespace '${K8S_NAMESPACE}'..."
                    sh """
                        kubectl get namespace ${K8S_NAMESPACE} || kubectl create namespace ${K8S_NAMESPACE}
                    """
                }
            }
        }

        // ✅ Stage 4: Deploy to Kubernetes (Dynamic Deployment)
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "🚀 Deploying app to Kubernetes in namespace '${K8S_NAMESPACE}'..."

                    // Use envsubst for multiple env replacements instead of sed
                    sh """
                        export IMAGE=${IMAGE_NAME}:${BRANCH_NAME}
                        export NAMESPACE=${K8S_NAMESPACE}

                        # Replace placeholders dynamically
                        envsubst < k8s/deployment.yaml > k8s/deployment_temp.yaml

                        # Apply Deployment and Service
                        kubectl apply -f k8s/deployment_temp.yaml -n \$NAMESPACE
                        kubectl apply -f k8s/service.yaml -n \$NAMESPACE

                        # Optional: Rollout status for fail-safe deployments
                        kubectl rollout status deployment/todo-app -n \$NAMESPACE --timeout=60s
                    """
                }
            }
        }

        // ✅ Stage 5: Health Check on Kubernetes
        stage('Health Check') {
            steps {
                script {
                    echo "🔍 Performing Kubernetes deployment health check..."
                    sh """
                        sleep 10  # Allow pods to come up

                        echo "📊 Pods status:"
                        kubectl get pods -n ${K8S_NAMESPACE}

                        # Dynamic pod name fetching and logs
                        POD_NAME=\$(kubectl get pods -n ${K8S_NAMESPACE} -l app=todo-app -o jsonpath="{.items[0].metadata.name}")
                        echo "📜 Logs from Pod \$POD_NAME:"
                        kubectl logs \$POD_NAME -n ${K8S_NAMESPACE}

                        # Check if pod is ready
                        kubectl wait --for=condition=ready pod/\$POD_NAME --timeout=60s -n ${K8S_NAMESPACE}

                        # Get Service status
                        echo "🌐 Service status:"
                        kubectl get svc -n ${K8S_NAMESPACE}

                        echo '✅ App successfully deployed and running on Kubernetes.'
                    """
                }
            }
        }
    }

    // ✅ Post actions for notifications
    post {
        success {
            echo "🎉 Deployment successful for branch: ${BRANCH_NAME}!"
        }
        failure {
            echo "❌ Deployment failed for branch: ${BRANCH_NAME}. Check Jenkins logs for details."
        }
        always {
            echo "📜 Pipeline completed for branch: ${BRANCH_NAME}."
        }
    }
}