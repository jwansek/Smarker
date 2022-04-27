# Smarker
An automated marking system for UEA programming assessments

## Running in docker

`sudo docker run -v "$(pwd)/../wsData.txt":/wsData.txt -v "$(pwd)/100301654.zip":/tmp/100301654.zip -v "$(pwd)/out/":/out/ -e submission=/tmp/100301654.zip -e assessment=example -e SMARKERDEPS=matplotlib -e format=pdf -e output=/out/100301654.pdf --rm smarker`

`sudo docker run -it --entrypoint python --rm smarker assessments.py --list yes`