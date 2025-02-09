#!/usr/bin/python3
import argparse
import importlib
import time
import os
import sys
import logging
import json
from pyspark.sql import SparkSession
import logging.config
import logging

if os.path.exists("libs.zip"):
    sys.path.insert(0, "libs.zip")
else:
    sys.path.insert(0, "./libs")

if os.path.exists("jobs.zip"):
    sys.path.insert(0, "jobs.zip")
else:
    sys.path.insert(0, "./jobs")

try:
    import pyspark
except ImportError:
    import findspark

    findspark.init()
    import pyspark

__author__ = "nguyendt"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a PySpark job")
    parser.add_argument(
        "--job",
        type=str,
        required=True,
        dest="job_name",
        help="The name of the job module you want to run. (ex: poc will run job on jobs.poc package)",
    )
    parser.add_argument(
        "--job-args",
        nargs="*",
        help="Extra arguments to send to the PySpark job (example: --job-args template=manual-email1 foo=bar",
    )

    args = parser.parse_args()
    print("Called with arguments: %s" % args)

    environment = {"PYSPARK_JOB_ARGS": " ".join(args.job_args) if args.job_args else ""}

    job_args = dict()
    if args.job_args:
        job_args_tuples = [arg_str.split("=") for arg_str in args.job_args]
        print("job_args_tuples: %s" % job_args_tuples)
        job_args = {a[0]: a[1] for a in job_args_tuples}

    print("\nRunning job %s...\nenvironment is %s\n" % (args.job_name, environment))
    os.environ.update(environment)
    
    spark = SparkSession.builder.appName(args.job_name).getOrCreate()
    job_module = importlib.import_module("jobs.%s" % args.job_name)
 

    # get logging config file
    with open('./logging.json') as log_json:
        logging_config = json.load(log_json)
    logging.config.dictConfig(logging_config)
    logger_main = logging.getLogger(__name__)

    # # to test various levels
    # logger_main.debug('debug message')
    # logger_main.info('info message')
    # logger_main.warn('warn message')
    # logger_main.error('error message')
    # logger_main.critical('critical message') 
    # initialize  logger for yarn cluster logs
    log4jLogger = spark._jvm.org.apache.log4j
    logger_pyspark = log4jLogger.LogManager.getLogger(__name__)
    logger_pyspark.info("pyspark script logger initialized")
    start = time.time()
    job_module.analyze(spark, **job_args)
    end = time.time()

    print("\nExecution of job %s took %s seconds" % (args.job_name, end - start))
