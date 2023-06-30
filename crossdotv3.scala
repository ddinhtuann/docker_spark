import org.apache.spark.ml.linalg.Vector
import org.apache.spark.sql.functions._
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
      .set("spark.memory.fraction", "0.81")
      .set("spark.sql.shuffle.partitions", "40")
      .set("spark.sql.tungsten.enable", "true")
      .set("spark.file.transferTo", "false")
    val spark = SparkSession.builder()
      .config(conf)
      .getOrCreate()

    //val dotProduct = udf((v1: Vector, v2: Vector) => v1.dot(v2))
    val df_vector = spark.read.json("hdfs://namenode37:9000/user/coretech/sample.json").withColumn("size", size(col("embedding")))//.withColumn("embedding", array_to_vector(col("embedding")))
    
    val df1 = df_vector.as("df1")
    val df2 = df_vector.as("df2")

    val dot = df1.join(df2, col("df1.id") < col("df2.id") && col("df1.size") === col("df2.size")).select(col("df1.id").as("id"), col("df2.id").as("id2"), expr("aggregate(zip_with(df1.embedding, df2.embedding, (x, y) -> x * y), 0D, (sum, x) -> sum + x)").as("crossDotProduct"))

    dot.cache()
    
    val dot_fil = dot.filter(col("crossDotProduct")>0.5)
    dot_fil.repartition(80)

    val dot_sort = dot_fil.orderBy(desc("crossDotProduct"))

    dot_sort.persist(StorageLevel.MEMORY_AND_DISK)
    val output = dot_sort.takeAsList(100)
    // dot_fil.show()
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