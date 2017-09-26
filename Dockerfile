
# debian & python3.6
FROM python:3.6

# add mongodb to sources list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
RUN echo "deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/3.4 main" | tee /etc/apt/sources.list.d/mongodb-org-3.4.list
RUN apt-get update && apt-get -y upgrade

# mongodb
RUN apt-get install -y mongodb-org
RUN mkdir -p /data/db

# add baemo
ADD ./baemo /baemo/baemo
ADD ./setup.py /baemo/setup.py

# install baemo
WORKDIR /baemo
RUN pip install .[tests]

# tests
ADD ./test /test

# run
CMD ["mongod"]
