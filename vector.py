from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql import SparkSession

sc =  SparkSession.builder.master("spark://10.0.68.37:8077").appName("accross").config("spark.driver.bindAddress", "127.0.0.1").getOrCreate()
df = sc.read.option("multiline", "true").json("file:///usr/share/Handwritten-digits-classification-pyspark/sample.json")
df.show()
