pipeline {
    agent any

    stages {

        stage('Checkout code from GitHub') {
            steps {
                git branch: 'main', url: 'https://github.com/tuheen27/Dev-Ops-security-playground.git'
            }
        }

        stage('Build the application') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    pip install .
                    python app.py
                '''
                echo 'build completed!'            }
        }
    }

    post {
        always {
            echo 'This is a simple pipeline to learn the Jenkinsfile syntax'
        }
    }
}
