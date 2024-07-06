from datetime import datetime

from common.lib.logger import Log4j
from common.lib.SparkSession import getSparkSession
import sys
from common.lib.loggingSession import *
import pyspark.sql.functions as F
from pyspark.sql import Window
from pyspark.sql.functions import col, current_date, datediff
from pyspark.sql.types import StringType

cnt = 0

def cast_booking_data(bookings):
    try:
        logger = getloggingSession()
        logger.info("Parsing passenger data 1...!!!")
        booking_df_casted_1 = bookings. \
            withColumn("ts_date_created", (col("date_created")).cast("timestamp")). \
            withColumn("ts_date_close", (col("date_close")).cast("timestamp"))

        booking_df_casted_1.show()

        logger.info("Parsing passenger data 2...!!!")

        booking_df_casted_2 = booking_df_casted_1.withColumn("dt_date_created", (col("date_created")).cast("date"))

        booking_df_casted_2.show()

        logger.info("Parsing passenger data - final...!!!")

        booking_df_casted = booking_df_casted_2.drop(col("id")).drop(col("id_passenger"))

    except Exception as e:
        logger.info("Failed to Parse passenger data..aborting...!!!")
        sys.exit(400)

    return booking_df_casted


if __name__ == "__main__":
    # generic module to start Spark session and logging
    spark = getSparkSession("booking")
    logger = Log4j(spark)
    prog_start = datetime.now()
    print("Spark job starts here")

    try:
        logger = getloggingSession()
        logger.info("Reading booking data from source file ...!!!")
        bookings = spark.read.option("header", True).csv("./common/data/resource/booking_data.csv")
    except Exception as e:
        logger.info("Failed to read booking data from source file..aborting...!!!")
        sys.exit(400)

    booking_df_casted = cast_booking_data(bookings)
    booking_df_casted.show()

    booking_df_casted.write.parquet("./common/data/result/booking_df_casted")

    try:
        logger = getloggingSession()
        logger.info("Writing resultant dataframe into target file ...!!!")
        booking_df_casted.coalesce(1).write.mode("overwrite").parquet("./common/data/result/booking_df_casted")
        # booking_df_casted.coalesce(1). \
        #     write. \
        #     option("header", "true"). \
        #     mode("overwrite"). \
        #     csv("./common/data/result/booking_df_casted.csv")
    except Exception as e:
        logger.info("Failed to write resultant data into target file..aborting...!!!")
        sys.exit(400)

    print('Total execution time - ', (datetime.now() - prog_start))

spark.catalog.clearCache()
spark.stop()
