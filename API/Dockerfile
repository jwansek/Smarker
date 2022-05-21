FROM smarker
MAINTAINER Eden Attenborough "gae19jtu@uea.ac.uk"
COPY . /API
WORKDIR /API
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py", "--production"]