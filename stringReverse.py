import sys
from pyspark.sql.types import *
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, SQLContext
from pyspark.streaming import StreamingContext
import matplotlib.pyplot as plt
import pandas
from pyspark.sql.functions import col, concat, reverse, column
import os
import json
import kafka
import collections
from collections import Counter
import cv2
import base64
import json
import time
import threading, logging, time
# from confluent_kafka import Consumer as KafkaConsumer, Producer as KafkaProducer
from kafka import KafkaConsumer as KafkaConsumer1, KafkaProducer as KafkaProducer1
import gc
import sys
import os
from PIL import Image
from PIL import ImageFile
import threading
from threading import Lock
import youtube_dl
import pafy
import numpy as np
from pyspark.sql import SparkSession


os.environ["SPARK_HOME"] = "/spark"

conf = SparkConf()
conf.setMaster("spark://172.24.0.2:7077").setAppName("test") \
.set("spark.executor.heartbeatInterval", "10000000").set("spark.network.timeout", "100000000").set("spark.executor.memory", "14g").set('spark.driver.memory', '8g').set("spark.eventLog.enabled", "true").set("spark.cores.max", "24")
time_start = time.time()
sc = SparkContext.getOrCreate(conf=conf)
    
class dataInput:
    def stringInput(self):
        data = sc.textFile("text2mb.txt")
        data = data.collect()
        rddPartition = sc.parallelize(data, 3)
        rddPartition.foreach(lambda x: process().reverse(x))
        time.sleep(50)

class process:
    def reverse(self, record):
        words = record.split(" ")
        wordsReverseArr = []
        stringReverse = ""
        for i in words:
            wordsReverseArr.append(i[::-1])
        
        for i in wordsReverseArr:
            stringReverse = stringReverse + str(i) + "\n "             
        
        print('Reverse: ',stringReverse)

if __name__ == '__main__':
    a = dataInput()
    a.stringInput()