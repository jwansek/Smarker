tar czvf build.tar.gz build/
scp build.tar.gz eden@vps.eda.gay:/home/eden/SmarkerDocs/build.tar.gz
rm build.tar.gz
ssh eden@vps.eda.gay "rm -rf /home/eden/SmarkerDocs/build/"
ssh eden@vps.eda.gay "tar xvf /home/eden/SmarkerDocs/build.tar.gz -C /home/eden/SmarkerDocs"
ssh eden@vps.eda.gay "rm /home/eden/SmarkerDocs/build.tar.gz"
ssh eden@vps.eda.gay "chmod 755 -R /home/eden/SmarkerDocs/build/"