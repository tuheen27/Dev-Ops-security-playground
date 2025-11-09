pipeline {
                agent any
                stages {
                                stage{
                                                (checkout codefrom github){
steps{
                git  branch: 'main', url: 'https://github.com/tuheen27/Dev-Ops-security-playground.git'
}
                                                }
                                }
                                stage(build the application){
                                                stpps{
                                                                sh '''
                                                                pip install -r requirements.txt
                                                                pip install 
                                                                '''
                                                }
                                }

                }
}

post{
                alawyays{
                                echo 'this is simple  pipeline to learn the jenkins file syntax' 
                }
}
