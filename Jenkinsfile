pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'security-playground'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        PYTHON_VERSION = '3.9'
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo 'Checking out code from GitHub...'
                git branch: 'main', url: 'https://github.com/tuheen27/Dev-Ops-security-playground.git'
                echo 'Checkout completed successfully!'
            }
        }

        stage('Verify Environment') {
            steps {
                echo 'Verifying Python and Docker installation...'
                sh '''
                    python3 --version
                    pip3 --version
                    docker --version
                '''
                echo 'Environment verification completed!'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    # Create virtual environment
                    python3 -m venv venv || echo "Virtual environment already exists"
                    
                    # Activate and install dependencies
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    # Verify installation
                    pip list
                '''
                echo 'Dependencies installed successfully!'
            }
        }

        stage('Syntax Check') {
            steps {
                echo 'Checking Python syntax...'
                sh '''
                    . venv/bin/activate
                    python3 -m py_compile app.py
                '''
                echo 'Syntax check passed!'
            }
        }

        stage('Security Scan') {
            steps {
                echo 'Running security checks...'
                sh '''
                    . venv/bin/activate
                    # Install safety for dependency vulnerability scanning
                    pip install safety || true
                    safety check --json || echo "Security scan completed with warnings"
                '''
                echo 'Security scan completed!'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh """
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                """
                echo 'Docker image built successfully!'
            }
        }

        stage('Test Docker Image') {
            steps {
                echo 'Testing Docker image...'
                sh """
                    # Run container in detached mode
                    docker run -d --name test-container-${BUILD_NUMBER} -p 8080:8080 ${DOCKER_IMAGE}:${DOCKER_TAG}
                    
                    # Wait for container to start
                    sleep 5
                    
                    # Test health endpoint
                    curl -f http://localhost:8080/health || exit 1
                    
                    # Stop and remove test container
                    docker stop test-container-${BUILD_NUMBER}
                    docker rm test-container-${BUILD_NUMBER}
                """
                echo 'Docker image tests passed!'
            }
        }

        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    // This is a placeholder - configure with your registry
                    echo "Would push ${DOCKER_IMAGE}:${DOCKER_TAG} to registry"
                    // docker.withRegistry('https://your-registry.com', 'credentials-id') {
                    //     docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                    // }
                }
                echo 'Push stage completed!'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying application...'
                script {
                    // This is a placeholder - configure with your deployment method
                    echo "Would deploy ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    // Add your deployment commands here (k8s, docker-compose, etc.)
                }
                echo 'Deployment stage completed!'
            }
        }

    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo "Docker image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
        }
        failure {
            echo '❌ Pipeline failed! Check logs for details.'
        }
        always {
            echo 'Cleaning up...'
            sh '''
                # Clean up virtual environment
                rm -rf venv || true
                
                # Clean up any leftover test containers
                docker ps -a | grep test-container-${BUILD_NUMBER} | awk '{print $1}' | xargs docker rm -f || true
                
                # Optional: Clean up old Docker images
                # docker image prune -f
            '''
            echo 'Pipeline execution completed - Security Playground Jenkins Pipeline'
        }
    }
}
