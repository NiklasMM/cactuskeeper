pipeline {
    agent none
    stages {
        stage('build') {
            parallel {
              stage('py2') {
                agent { docker { image 'python:2.7.12' }}
                steps { sh 'python --version' }
              }
              stage('py3') {
                agent { docker { image 'python:3.5.1' }}
                steps { sh 'python --version' }
              }
            }
        }
    }
}
