package batdongsan

import java.io.IOException
import java.text.DecimalFormat
import org.apache.hadoop.fs.{FileSystem, Path}
import org.apache.log4j.{Level, Logger}
import org.apache.spark.sql.SparkSession
import org.apache.spark.{SparkConf, SparkContext}

object batdongsan {

  def main(args: Array[String]) {
    Logger.getLogger("org").setLevel(Level.ERROR)
    val conf = new SparkConf().setAppName("batdongsan").setMaster("local[*]")
    val sc = new SparkContext(conf)
    val session = SparkSession.builder().appName("batdongsan").master("local[1]").getOrCreate()
    val lines = sc.textFile("in/batdongsan.csv")

    val rdd = lines.filter(line => !line.contains("URL╡Name╡Mobile"))
      .filter(line => line.split("╡").length == 3)
      .map(line => {
        val splits = line.split("╡")
        val len = splits.length
        (splits(0), splits(len-1).trim.replaceAll("[^0-9]", ""))
      })
      .reduceByKey((x,y) => x)

    val mobileCount = rdd.map(x => (x._2, 1))
      .reduceByKey((x,y) => x+y)
      .sortBy(x => x._2, ascending = false)

    //mobileCount.coalesce(1).saveAsTextFile("out/mobile_count.csv")

    val companyCount = mobileCount.map(x => (1, x._1))
      .mapValues(number => number.slice(0,3))
      .mapValues(number =>
        if(
          number == "086" ||
            number == "096" ||
            number == "097" ||
            number == "098" ||
            number == "032" ||
            number == "033" ||
            number == "034" ||
            number == "035" ||
            number == "036" ||
            number == "037" ||
            number == "038" ||
            number == "039"
        ) "Viettel"
        else if(
          number == "089" ||
            number == "090" ||
            number == "093" ||
            number == "070" ||
            number == "079" ||
            number == "077" ||
            number == "078" ||
            number == "076"
        ) "MobiFone"
        else if(
          number == "088" ||
            number == "091" ||
            number == "094" ||
            number == "083" ||
            number == "084" ||
            number == "085" ||
            number == "081" ||
            number == "082"
        ) "VinaPhone"
        else if(
          number == "092" ||
            number == "056" ||
            number == "058"
        ) "Vietnammobile"
        else if(
          number == "099" ||
            number == "059"
        ) "Gmobile"
        else "None"
      )
      .map(x => (x._2, x._1))
      .reduceByKey((x,y) => x+y)

    //companyCount.coalesce(1).saveAsTextFile("out/company_count.csv")

    val decimal_format = new DecimalFormat("0.00")
    val total = mobileCount.count()
    val company_percentage = companyCount.mapValues(count =>
      decimal_format.format((count.toDouble/total.toDouble)*100))

    import session.implicits._
    val DF = company_percentage.toDF()

    try{
      DF.coalesce(1).write.mode("overwrite").format("csv").save("out/company_percentage")

      val fs = FileSystem.get(sc.hadoopConfiguration)
      val filePath = "out/company_percentage/"
      val fileName = fs.globStatus(new Path(filePath+"part*"))(0).getPath.getName

      fs.rename(new Path(filePath+fileName), new Path(filePath+"company_percentage.csv"))
    }catch{
      case e: IOException => e.printStackTrace
    }
  }
}
