import org.apache.spark.ml.linalg.Vector
import org.apache.spark.sql.functions._
import org.apache.spark.ml.functions._
import org.apache.spark.sql.expressions.Window

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

    //case class Doc(id: Int, embedding: Array)
    val conf = new SparkConf()
      .setAppName("crossdot")
      .set("spark.shuffle.file.buffer", "1m")
      .set("spark.sql.autoBroadcastHashJoinThreshold", "-1")
      //.set("spark.sql.files.maxPartitionBytes", "207456383")
      .set("spark.memory.fraction", "0.81")
      .set("spark.sql.shuffle.partitions", "53")
      .set("spark.sql.tungsten.enable", "true")
      .set("spark.file.transferTo", "false")
      //

      // .set("spark.serializer", "org.apache.spark.serializer.KyroSerializer")
      // .set("spark.kryo.registrationRequired", "true")
      // .registerKryoClasses( Array(classOf[Person],classOf[Array[Person]],
      // Class.forName("org.apache.spark.internal.io.FileCommitProtocol$TaskCommitMessage"))
      //     )
    val dotProduct = udf((v1: Vector, v2: Vector) => v1.dot(v2))
    val spark = SparkSession.builder()
      .config(conf)
      .getOrCreate()
    val windowSpec = Window.orderBy(desc("crossDotProduct"))
    
    var df_vector = spark.read.json("hdfs://namenode37:9000/user/coretech/sample.json").withColumn("size", size(col("embedding"))).withColumn("embedding", array_to_vector(col("embedding")))
    
    val df1 = df_vector.as("df1")
    val df2 = df_vector.as("df2")

    val dot = df1.join(df2, col("df1.id") < col("df2.id") && col("df1.size") === col("df2.size")).select(col("df1.id").as("id"), col("df2.id").as("id"), dotProduct(col("df1.embedding"), col("df2.embedding")).as("crossDotProduct"))
    dot.cache()

    val dot_fil = dot.filter(col("crossDotProduct")>0.5)
    dot_fil.repartition(80)

    val dot_sort = dot_fil.withColumn("rank", rank.over(windowSpec)).filter(col("rank") <= 100)
    dot_sort.persist(StorageLevel.MEMORY_AND_DISK)
    
    val output = dot_fil.takeAsList(100)
    // Chuyển đổi danh sách sang chuỗi JSON
    implicit val formats = DefaultFormats
    val jsonData = write(Map("data" -> output))

    val response = Http("http://spark-driver37:5000/getlist")
                      .postData(jsonData)
                      .header("content-type", "application/json")
                      .asString
              
    spark.stop()
  }
}