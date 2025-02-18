import streamlit as st
from constants import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
from sqlalchemy import create_engine 
import pandas as pd

connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(connection_string) #connectar till databas 

query = "SELECT * FROM shiba_inu;"


with engine.connect() as connect:
    df = pd.read_sql(query, connect)

st.markdown("# Shibu Inu data")
st.markdown("## latest data")

st.dataframe(df.head())



