import org.apache.spark.ml.linalg.Vector
import org.apache.spark.sql.functions._
import org.apache.spark.ml.functions._
import org.apache.spark.ml.functions._

import org.apache.spark.sql.SaveMode
import org.apache.spark.sql.SparkSession
import org.apache.spark.SparkConf

import org.apache.spark.storage.StorageLevel._
import org.apache.spark.storage.StorageLevel
import scala.collection._

import scalaj.http._

import org.json4s._
import org.json4s.jackson.Serialization.{write, read}


object CrossDot {
  def main(args: Array[String]) {
    val conf = new SparkConf()
      .setAppName("crossdot")
      .set("spark.shuffle.file.buffer", "1m")
      .set("spark.sql.autoBroadcastHashJoinThreshold", "-1")
      .set("spark.dynamicAllocation.enable", "false")
      //.set("spark.driver.host", "spark-worker40")
      //.set("spark.driver.port", "46849")  
      //.set("spark.driver.bindAddress", "10.0.1.50")
      //.set("spark.sql.files.maxPartitionBytes", "207456383")
      .set("spark.memory.fraction", "0.81")
      .set("spark.sql.shuffle.partitions", "53")
      .set("spark.sql.tungsten.enable", "true")
      .set("spark.file.transferTo", "false")
    val spark = SparkSession.builder()
      .config(conf)
      .getOrCreate()

    val dotProduct = udf((v1: Vector, v2: Vector) => v1.dot(v2))
    val df_vector = spark.read.json("hdfs://namenode37:9000/user/coretech/sample.json").withColumn("size", size(col("embedding"))).withColumn("embedding", array_to_vector(col("embedding")))
    df_vector.cache()
    val df1 = df_vector.as("df1")
    val df2 = df_vector.as("df2")
    
    //val df2 = df_vector.join(df1, col("df_vector.id") < col("df1.id") && col("df_vector.size") === col("df1.size"))
    
    val dot = df1.join(df2, col("df1.id") < col("df2.id") && col("df1.size") === col("df2.size")).select(col("df1.id").as("id"), col("df2.id").as("id2"), dotProduct(col("df1.embedding"), col("df2.embedding")).as("crossDotProduct"))

    val dot_fil = dot.filter(col("crossDotProduct")>0.5)
    
    val dot_sort = dot_fil.orderBy(col("crossDotProduct").desc)
    dot_sort.coalesce(14)
    dot_sort.persist(StorageLevel.MEMORY_AND_DISK)
    val output = dot_fil.takeAsList(100)

    // Chuyển đổi danh sách sang chuỗi JSON
    implicit val formats = DefaultFormats
    val jsonData = write(Map("data" -> output))

    val response = Http("http://spark-driver40:5000/getlist")
                      .postData(jsonData)
                      .header("content-type", "application/json")
                      .asString
              
    spark.stop()
    // Chuyển đổi danh sách sang chuỗi JSON
     
  }
}


