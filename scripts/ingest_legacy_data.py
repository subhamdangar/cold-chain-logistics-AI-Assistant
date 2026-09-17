from pathlib import Path
import os
import urllib

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

env_path = project_root / ".env"
load_dotenv(env_path)

print(f"Loading environment file from: {env_path}")
print(f".env exists: {env_path.exists()}")


data_path = (
    project_root
    / "data"
    / "raw"
    / "dynamic_supply_chain_logistics_dataset.csv"
)


db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "1433")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

if not db_user or not db_password:
    raise ValueError(
        "DB_USER or DB_PASSWORD is missing from the .env file."
    )


# 1. Load the raw dataset
print(f"Loading CSV from {data_path}...")

df = pd.read_csv(data_path)

print(f"Loaded {len(df)} rows.")


# 2. Map the dataset to the legacy enterprise schema
legacy_mapping = {
    "timestamp": "TS_UTC",
    "vehicle_gps_latitude": "V_LAT",
    "vehicle_gps_longitude": "V_LON",
    "iot_temperature": "IOT_TEMP_VAL_C",
    "cargo_condition_status": "CGO_COND_CD",
    "risk_classification": "RISK_CLS_TXT",
    "delay_probability": "DELAY_PROB_DEC",
    "port_congestion_level": "PRT_CNG_LVL",
    "route_risk_level": "RT_RSK_IDX",
}

df_legacy = (
    df[list(legacy_mapping.keys())]
    .rename(columns=legacy_mapping)
)

df_legacy["SYS_INGEST_FLAG"] = "Y"


# 3. Connect to SQL Server
print("Connecting to legacy MSSQL Database...")

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={db_host},{db_port};"
    "DATABASE=SupplyChainDB;"
    f"UID={db_user};"
    f"PWD={db_password};"
    "Encrypt=no;"
    "TrustServerCertificate=yes;"
)

params = urllib.parse.quote_plus(connection_string)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}"
)


# 4. Insert data into the legacy table
table_name = "TBL_SC_FLEET_HIST_RAW"

print(f"Ingesting data into {table_name}...")

df_legacy.to_sql(
    table_name,
    engine,
    if_exists="replace",
    index=False,
    schema="dbo",
)

print("Legacy data ingestion complete!")
print(f"Rows inserted: {len(df_legacy)}")