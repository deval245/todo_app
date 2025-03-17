pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-cred')
        GITHUB_CREDENTIALS = credentials('github-cred')
        IMAGE_NAME = "devalth/todo-app"
        BRANCH_NAME = "${env.BRANCH_NAME}"
        K8S_NAMESPACE = "todo-app-${env.BRANCH_NAME}"  // ✅ Separate namespace per branch
        KUBECONFIG = "/root/.kube/config"  // ✅ Jenkins K8s config location
    }

    stages {

        // ✅ Checkout Code
        stage('Checkout Code') {
            steps {
                echo "🧾 Checking out branch: ${BRANCH_NAME}"
                git branch: "${BRANCH_NAME}", credentialsId: "${GITHUB_CREDENTIALS}", url: 'https://github.com/deval245/todo_app.git'
            }
        }

        // ✅ Build and Push Docker Image
        stage('Build & Push Docker Image') {
            steps {
                script {
                    echo '🐳 Building & pushing Docker image to DockerHub...'
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

        // ✅ Create Namespace if Not Exists
        stage('Create Namespace') {
            steps {
                script {
                    echo "📦 Ensuring namespace '${K8S_NAMESPACE}' exists..."
                    sh """
                        kubectl get namespace ${K8S_NAMESPACE} || kubectl create namespace ${K8S_NAMESPACE}
                    """
                }
            }
        }

        // ✅ Deploy to Kubernetes
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "🚀 Deploying to namespace '${K8S_NAMESPACE}'..."
                    sh """
                        # 🔁 Replace placeholders in deployment.yaml
                        sed 's|IMAGE_PLACEHOLDER|${IMAGE_NAME}:${BRANCH_NAME}|g; s|NAMESPACE_PLACEHOLDER|${K8S_NAMESPACE}|g' k8s/deployment.yaml > k8s/deployment_temp.yaml

                        # 🔁 Replace placeholders in service.yaml
                        sed 's|NAMESPACE_PLACEHOLDER|${K8S_NAMESPACE}|g' k8s/service.yaml > k8s/service_temp.yaml

                        # ✅ Apply namespace definition (if any)
                        kubectl apply -f k8s/namespace.yaml

                        # ✅ Apply deployment and service
                        kubectl apply -f k8s/deployment_temp.yaml
                        kubectl apply -f k8s/service_temp.yaml
                    """
                }
            }
        }

        // ✅ Health Check
        stage('Health Check') {
            steps {
                script {
                    echo "🔍 Checking app health in namespace '${K8S_NAMESPACE}'..."
                    sh """
                        sleep 10  # Give pods some time to start

                        echo "📊 Pod status:"
                        kubectl get pods -n ${K8S_NAMESPACE}

                        # ✅ Fetch first pod's name
                        POD_NAME=\$(kubectl get pods -n ${K8S_NAMESPACE} -l app=todo-app -o jsonpath="{.items[0].metadata.name}")

                        echo "📜 Pod logs:"
                        kubectl logs \$POD_NAME -n ${K8S_NAMESPACE}

                        # ✅ Wait for pod readiness
                        kubectl wait --for=condition=ready pod/\$POD_NAME --timeout=60s -n ${K8S_NAMESPACE}

                        echo "🌐 Service status:"
                        kubectl get svc -n ${K8S_NAMESPACE}

                        echo '✅ App is successfully running!'
                    """
                }
            }
        }
    }

    // ✅ Pipeline Post Steps
    post {
        success {
            echo "🎉 Success! App deployed on branch: ${BRANCH_NAME}"
        }
        failure {
            echo "❌ Deployment failed for branch: ${BRANCH_NAME}. Check logs!"
        }
        always {
            echo "📜 Pipeline finished for branch: ${BRANCH_NAME}"
        }
    }
}