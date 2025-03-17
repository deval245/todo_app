pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-cred')
        GITHUB_CREDENTIALS = credentials('github-cred')
        IMAGE_NAME = "devalth/todo-app"
        BRANCH_NAME = "${env.BRANCH_NAME}"
        K8S_NAMESPACE = "todo-app-${env.BRANCH_NAME}"  // ✅ Per branch namespace
        KUBECONFIG = "/root/.kube/config"  // ✅ K8s config for Jenkins
    }

    stages {

        // ✅ 1. Checkout Code
        stage('Checkout Code') {
            steps {
                echo "🧾 Checking out branch: ${BRANCH_NAME}"
                git branch: "${BRANCH_NAME}", credentialsId: "${GITHUB_CREDENTIALS}", url: 'https://github.com/deval245/todo_app.git'
            }
        }

        // ✅ 2. Build and Push Docker Image
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

        // ✅ 3. Create Namespace
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

        // ✅ 4. Deploy Postgres to Kubernetes
        stage('Deploy Postgres') {
            steps {
                script {
                    echo "🐘 Deploying PostgreSQL in namespace '${K8S_NAMESPACE}'..."
                    sh """
                        # 🔁 Replace namespace in Postgres deployment and service
                        sed 's|NAMESPACE_PLACEHOLDER|${K8S_NAMESPACE}|g' k8s/postgres-deployment.yaml > k8s/postgres-deployment-temp.yaml
                        sed 's|NAMESPACE_PLACEHOLDER|${K8S_NAMESPACE}|g' k8s/postgres-service.yaml > k8s/postgres-service-temp.yaml

                        # ✅ Apply Postgres deployment and service
                        kubectl apply -f k8s/postgres-deployment-temp.yaml
                        kubectl apply -f k8s/postgres-service-temp.yaml
                    """
                }
            }
        }

        // ✅ 5. Deploy App to Kubernetes
        stage('Deploy App to Kubernetes') {
            steps {
                script {
                    echo "🚀 Deploying App to namespace '${K8S_NAMESPACE}'..."
                    sh """
                        # 🔁 Replace placeholders in deployment.yaml
                        sed 's|IMAGE_PLACEHOLDER|${IMAGE_NAME}:${BRANCH_NAME}|g; s|NAMESPACE_PLACEHOLDER|${K8S_NAMESPACE}|g' k8s/deployment.yaml > k8s/deployment_temp.yaml

                        # 🔁 Replace namespace in service.yaml
                        sed 's|NAMESPACE_PLACEHOLDER|${K8S_NAMESPACE}|g' k8s/service.yaml > k8s/service_temp.yaml

                        # ✅ Apply App deployment and service
                        kubectl apply -f k8s/deployment_temp.yaml
                        kubectl apply -f k8s/service_temp.yaml
                    """
                }
            }
        }

        // ✅ 6. Health Check (Postgres + App)
        stage('Health Check') {
            steps {
                script {
                    echo "🔍 Performing health check in namespace '${K8S_NAMESPACE}'..."
                    sh """
                        sleep 10  # Wait for pods to start

                        echo "📊 Pod status:"
                        kubectl get pods -n ${K8S_NAMESPACE}

                        # ✅ App Pod Health Check
                        APP_POD_NAME=\$(kubectl get pods -n ${K8S_NAMESPACE} -l app=todo-app -o jsonpath="{.items[0].metadata.name}")
                        echo "📜 App Pod logs:"
                        kubectl logs \$APP_POD_NAME -n ${K8S_NAMESPACE}
                        kubectl wait --for=condition=ready pod/\$APP_POD_NAME --timeout=60s -n ${K8S_NAMESPACE}

                        # ✅ Optional: Postgres Pod Health Check
                        POSTGRES_POD_NAME=\$(kubectl get pods -n ${K8S_NAMESPACE} -l app=todo-postgres -o jsonpath="{.items[0].metadata.name}")
                        echo "📜 Postgres Pod logs:"
                        kubectl logs \$POSTGRES_POD_NAME -n ${K8S_NAMESPACE}
                        kubectl wait --for=condition=ready pod/\$POSTGRES_POD_NAME --timeout=60s -n ${K8S_NAMESPACE}

                        # ✅ Final Service Check
                        echo "🌐 Services:"
                        kubectl get svc -n ${K8S_NAMESPACE}

                        echo '✅ App and Postgres are running successfully!'
                    """
                }
            }
        }
    }

    // ✅ 7. Post Actions
    post {
        success {
            echo "🎉 Success! Full stack (App + Postgres) deployed on branch: ${BRANCH_NAME}"
        }
        failure {
            echo "❌ Deployment failed for branch: ${BRANCH_NAME}. Check logs!"
        }
        always {
            echo "📜 Pipeline finished for branch: ${BRANCH_NAME}"
        }
    }
}