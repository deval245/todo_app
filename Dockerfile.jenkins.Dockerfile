# Start from Jenkins LTS official image
FROM jenkins/jenkins:lts

# Switch to root to install Docker CLI inside Jenkins container
USER root

# Install Docker CLI & Docker Compose inside Jenkins for building and pushing images
RUN apt-get update && \
    apt-get install -y docker.io docker-compose && \
    apt-get clean

# Optional: Add Jenkins user to Docker group (if needed for permissions)
RUN usermod -aG docker jenkins

# Switch back to Jenkins user for security
USER jenkins