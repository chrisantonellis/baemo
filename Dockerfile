
# debian & python3.6
FROM python:3.6

# add mongodb to sources list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
RUN echo "deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/3.4 main" | tee /etc/apt/sources.list.d/mongodb-org-3.4.list
RUN apt-get update && apt-get -y upgrade

# mongodb
RUN apt-get install -y mongodb-org
RUN mkdir -p /data/db

# pymongo basemodel
ADD ./pymongo_basemodel /pymongo_basemodel

# tests
ADD ./test /test

# requirements
ADD ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

# run
CMD ["mongod"]
