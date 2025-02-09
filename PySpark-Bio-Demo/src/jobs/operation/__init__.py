import re
import logging
from functools import partial
from shared.context import JobContext
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType,
    DoubleType,
)

__author__ = "nguyendt"
logger_1 = logging.getLogger(__name__)
Schema_operation = StructType(
    [
        StructField("Cust", StringType()),
        StructField("Project_ID", StringType()),
        StructField("BatchID", StringType()),
        StructField("Time stream", TimestampType()),
        StructField("Scan", DoubleType()),
        StructField("Aeration rate(Fg:L/h)", DoubleType()),
        StructField("Agitator RPM(RPM:RPM)", DoubleType()),
        StructField("Sugar feed rate(Fs:L/h)", DoubleType()),
        StructField("Acid flow rate(Fa:L/h)", DoubleType()),
        StructField("Base flow rate(Fb:L/h)", DoubleType()),
        StructField("Heating/cooling water flow rate(Fc:L/h)", DoubleType()),
        StructField("Heating water flow rate(Fh:L/h)", DoubleType()),
        StructField("Water for injection/dilution(Fw:L/h)", DoubleType()),
        StructField("Air head pressure(pressure:bar)", DoubleType()),
        StructField("Dumped broth flow(Fremoved:L/h)", DoubleType()),
        StructField("Substrate concentration(S:g/L)", DoubleType()),
        StructField("Dissolved oxygen concentration(DO2:mg/L)", DoubleType()),
        StructField("Vessel Volume(V:L)", DoubleType()),
        StructField("Vessel Weight(Wt:Kg)", DoubleType()),
        StructField("pH(pH:pH)", DoubleType()),
        StructField("Temperature(T:K)", DoubleType()),
        StructField("Generated heat(Q:kJ)", DoubleType()),
        StructField("carbon dioxide percent in off-gas(CO2outgas:%)", DoubleType()),
        StructField("PAA flow(Fpaa:PAA flow (L/h))", DoubleType()),
        StructField(
            "PAA concentration offline(PAA_offline:PAA (g L^{-1}))", DoubleType()
        ),
        StructField("Oil flow(Foil:L/hr)", DoubleType()),
        StructField(
            "NH_3 concentration off-line(NH3_offline:NH3 (g L^{-1}))", DoubleType()
        ),
        StructField("Oxygen Uptake Rate(OUR:(g min^{-1}))", DoubleType()),
        StructField("Oxygen in percent in off-gas(O2:O20(%))", DoubleType()),
        StructField(
            "Offline Penicillin concentration(P_offline:P(g L^{-1}))", DoubleType()
        ),
        StructField(
            "Offline Biomass concentratio(X_offline:X(g L^{-1}))", DoubleType()
        ),
        StructField("Carbon evolution rate(CER:g/h)", DoubleType()),
        StructField("Ammonia shots(NH3_shots:kgs)", DoubleType()),
        StructField("Viscosity(Viscosity_offline:centPoise)", DoubleType()),
        StructField("Fault reference(Fault_ref:Fault ref)", DoubleType()),
        StructField(
            "0 - Recipe driven 1 - Operator controlled(Control_ref:Control ref)",
            DoubleType(),
        ),
        StructField("1- No Raman spec", DoubleType()),
        StructField(" 1-Raman spec recorded", DoubleType()),
        StructField("Batch reference(Batch_ref:Batch ref)", DoubleType()),
        StructField("Fault flag", DoubleType()),
    ]
)


API_URL = "http://endpoint-operation:8000/predict"



# API Call Function
def send_to_api(batch_iterator):
    import httpx
    client = httpx.Client(timeout=5.0)
    batch_data = [[row.asDict() if isinstance(row, Row) else row for row in batch_iterator]]
    predictions = []
    if batch_data:
        try:
            operation_metrics = {"data": batch_data}
            response = client.post(API_URL, json=operation_metrics)
            if response.status_code == 200:
                predictions = response.json()
                
        except Exception as e:
            print(f"Error calling API: {e}")
    else:
        logger_1.warn("Input data is null")
    client.close()
    return predictions
    

# UDF to call FastAPI
@udf(FloatType())
def predict_udf(data):
    response = send_to_api(iter(data))
    return response[0]["Predict"] if response else 0.0
    

# Function to Write Each Micro-Batch to PostgreSQL
jdbc_url = "jdbc:postgresql://ktech_postgresql:5432/bio"
connection_properties = {
    "user": "admin",
    "password": "admin",
    "driver": "org.postgresql.Driver"
}

def write_to_postgres(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "operation_db") \
        .option("user", connection_properties["user"]) \
        .option("password", connection_properties["password"]) \
        .option("driver", connection_properties["driver"]) \
        .mode("append") \
        .save()
        
def analyze(sc):

    logger_1.info("inside analyze editor")
    df = (
        sc.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "ktech_kafka:9092")
        .option("subscribe", "operation_metric")
        .load()
    )

    data = df.select(
        from_json(col("value").cast("string"), Schema_operation).alias("data")
    ).select("data.*")
    feature_cols = ["Sugar feed rate(Fs:L/h)",
            "Water for injection/dilution(Fw:L/h)","Substrate concentration(S:g/L)","Temperature(T:K)","Dissolved oxygen concentration(DO2:mg/L)","Vessel Volume(V:L)","pH(pH:pH)"]
    data = data.withColumn("prediction", predict_udf(struct(feature_cols)))
    
    column_mapping = {
    "Time stream": "Time_stream",
    "Aeration rate(Fg:L/h)": "Aeration_rate",
    "Agitator RPM(RPM:RPM)": "Agitator_RPM",
    "Sugar feed rate(Fs:L/h)": "Sugar_feed_rate",
    "Acid flow rate(Fa:L/h)": "Acid_flow_rate",
    "Base flow rate(Fb:L/h)": "Base_flow_rate",
    "Heating/cooling water flow rate(Fc:L/h)": "Heating_cooling_water_flow_rate",
    "Heating water flow rate(Fh:L/h)": "Heating_water_flow_rate",
    "Water for injection/dilution(Fw:L/h)": "Water_for_injection_dilution",
    "Air head pressure(pressure:bar)": "Air_head_pressure",
    "Dumped broth flow(Fremoved:L/h)": "Dumped_broth_flow",
    "Substrate concentration(S:g/L)": "Substrate_concentration",
    "Dissolved oxygen concentration(DO2:mg/L)": "Dissolved_oxygen_concentration",
    "Vessel Volume(V:L)": "Vessel_Volume",
    "Vessel Weight(Wt:Kg)": "Vessel_Weight",
    "pH(pH:pH)": "pH",
    "Temperature(T:K)": "Temperature",
    "Generated heat(Q:kJ)": "Generated_heat",
    "carbon dioxide percent in off-gas(CO2outgas:%)": "CO2_outgas",
    "PAA flow(Fpaa:PAA flow (L/h))": "PAA_flow",
    "PAA concentration offline(PAA_offline:PAA (g L^{-1}))": "PAA_concentration_offline",
    "Oil flow(Foil:L/hr)": "Oil_flow",
    "NH_3 concentration off-line(NH3_offline:NH3 (g L^{-1}))": "NH3_concentration_offline",
    "Oxygen Uptake Rate(OUR:(g min^{-1}))": "Oxygen_Uptake_Rate",
    "Oxygen in percent in off-gas(O2:O20(%))": "Oxygen_in_percent_in_off_gas",
    "Offline Penicillin concentration(P_offline:P(g L^{-1}))": "Offline_Penicillin_concentration",
    "Offline Biomass concentratio(X_offline:X(g L^{-1}))": "Offline_Biomass_concentration",
    "Carbon evolution rate(CER:g/h)": "Carbon_evolution_rate",
    "Ammonia shots(NH3_shots:kgs)": "Ammonia_shots",
    "Viscosity(Viscosity_offline:centPoise)": "Viscosity",
    "Fault reference(Fault_ref:Fault ref)": "Fault_reference",
    "0 - Recipe driven 1 - Operator controlled(Control_ref:Control ref)": "Control_reference",
    "1- No Raman spec": "No_Raman_spec",
    "1-Raman spec recorded": "Raman_spec_recorded",
    "Batch reference(Batch_ref:Batch ref)": "Batch_reference",
    "Fault flag": "Fault_flag"
    }

    for old_name, new_name in column_mapping.items():
        data = data.withColumnRenamed(old_name, new_name)
        
    query = data.writeStream \
        .outputMode("append") \
        .foreachBatch(write_to_postgres) \
        .start()

    query.awaitTermination()
    # .trigger(continuous="1 second")