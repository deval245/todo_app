# Start from Jenkins LTS image
FROM jenkins/jenkins:lts

# Switch to root to install Docker CLI, Docker Compose, and kubectl inside Jenkins
USER root

# Install Docker CLI, Docker Compose
RUN apt-get update && \
    apt-get install -y docker.io docker-compose curl && \
    apt-get clean

# Install kubectl (latest stable version)
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

# Add Jenkins user to Docker group to allow Jenkins to run Docker commands without sudo
RUN usermod -aG docker jenkins

# Switch back to Jenkins user for security
USER jenkins