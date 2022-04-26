FROM ubuntu:latest
MAINTAINER Eden Attenborough "gae19jtu@uea.ac.uk"
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential texlive-base wkhtmltopdf
COPY ./Smarker /Smarker
WORKDIR /Smarker
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["smarker.py"]