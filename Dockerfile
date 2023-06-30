FROM openjdk:8u171-jre-stretch

# Add Dependencies for PySpark
RUN apt-get update && apt-get install -y curl vim wget software-properties-common ssh net-tools ca-certificates build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev \
libssl-dev libreadline-dev libffi-dev 
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get -y purge python3.5 && apt-get -y autoremove 
#RUN apt install -y python3.7 python3.7-distutils

##Install python3.7 on Debian 9
WORKDIR /usr/bin
RUN wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz

RUN tar xzf Python-3.7.2.tgz && rm Python-3.7.2.tgz

WORKDIR Python-3.7.2
RUN ./configure --enable-optimizations
RUN make altinstall
RUN alias python3=python3.7


#RUN update-alternatives --install "/usr/bin/python3" "python" "/usr/bin/python3.7" 0

#RUN apt-get update && apt-get install -y python3-pip
RUN pip3.7 install --upgrade pip

RUN pip3.7 install flask ujson requests hdfs==2.6.0


RUN wget https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz
RUN tar -xzf spark-3.1.2-bin-hadoop3.2.tgz && mv spark-3.1.2-bin-hadoop3.2 /spark && rm spark-3.1.2-bin-hadoop3.2.tgz
RUN mkdir /tmp/spark-events

# Fix the value of PYTHONHASHSEED
# Note: this is needed when you use Python 3.3 or greater
COPY start-master.sh /start-master.sh
COPY start-worker.sh /start-worker.sh
COPY api_spark.py /usr/share/Handwritten-digits-classification-pyspark/api_spark.py

RUN mkdir /usr/share/Handwritten-digits-classification-pyspark/jars
RUN mkdir /usr/share/Handwritten-digits-classification-pyspark/zip_folder
 
ENV PYSPARK_PYTHON=python3.7

EXPOSE 8080 4040 5001 7077







