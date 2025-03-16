# Start from Jenkins LTS image
FROM jenkins/jenkins:lts

# Switch to root to install Docker CLI and Docker Compose inside Jenkins
USER root

# Install Docker CLI and Docker Compose
RUN apt-get update && \
    apt-get install -y docker.io docker-compose && \
    apt-get clean

# Add Jenkins user to Docker group to allow Jenkins to run Docker commands without sudo
RUN usermod -aG docker jenkins

# Switch back to Jenkins user for security
USER jenkins