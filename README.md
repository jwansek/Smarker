# Smarker
An automated marking system for UEA programming assessments

## Running in docker

`sudo docker run -v "$(pwd)/../wsData.txt":/wsData.txt -v "$(pwd)/ExampleAssessments/CMP-4009B.yml":/tmp/CMP-4009.yml -v "$(pwd)/../ExampleSubmissions/123456789.zip":/tmp/123456789.zip -e submission=/tmp/123456789.zip -e assessment=/tmp/CMP-4009.yml -e SMARKERDEPS=matplotlib smarker`
