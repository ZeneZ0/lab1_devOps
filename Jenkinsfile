pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        IMAGE = 'lab1-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '. .venv/bin/activate && flake8 app tests'
            }
        }

        stage('Test') {
            steps {
                sh '. .venv/bin/activate && pytest -v --junitxml=reports/junit.xml'
            }
            post {
                always {
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('Build image') {
            when {
                anyOf { branch 'main'; branch 'dev' }
            }
            steps {
                sh 'docker build -t ${IMAGE}:${BRANCH_NAME}-${BUILD_NUMBER} .'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([string(credentialsId: 'lab1-db-password', variable: 'DB_PASS')]) {
                    sh '''
                        docker network inspect lab1-net >/dev/null 2>&1 || docker network create lab1-net

                        if [ -z "$(docker ps -aq -f name=^lab1-db$)" ]; then
                            docker run -d --name lab1-db --network lab1-net \
                                -e POSTGRES_USER=lab -e POSTGRES_PASSWORD="$DB_PASS" -e POSTGRES_DB=lab1 \
                                -v lab1_pg:/var/lib/postgresql/data postgres:16
                        fi
                        docker start lab1-db

                        docker rm -f lab1-app || true
                        docker run -d --name lab1-app --network lab1-net -p 8000:8000 --restart unless-stopped \
                            -e DATABASE_URL="postgresql+psycopg://lab:${DB_PASS}@lab1-db:5432/lab1" \
                            ${IMAGE}:${BRANCH_NAME}-${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Smoke test') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    for i in $(seq 1 15); do
                        docker exec lab1-app python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" && exit 0
                        sleep 2
                    done
                    docker logs lab1-app
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo "Сборка ${env.BRANCH_NAME} #${env.BUILD_NUMBER} прошла успешно"
        }
        failure {
            echo "Сборка ${env.BRANCH_NAME} #${env.BUILD_NUMBER} упала, деплой не выполнялся"
        }
    }
}
