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

# Växlingskurser (uppdatera vid behov)
USD_TO_SEK = 10.7
USD_TO_NOK = 11
USD_TO_DKK = 6.9

# Anslut till databasen
connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(connection_string)

# Hämta data från databasen
query = 'SELECT coin, price_usd, updated, timestamp FROM "XRP";'
with engine.connect() as connect:
    df = pd.read_sql(query, connect)

# Added online xrp logo 
st.image("https://cryptologos.cc/logos/xrp-xrp-logo.png", width=150)
st.markdown("# XRP Coin Data")
# Visa datan i Streamlit

# Skapa dropdown för val av valuta
currency = st.selectbox("Välj en valuta:", ["USD", "SEK", "NOK", "DKK"])
# Funktion för att konvertera priser
def convert_price(price_usd, currency):
    if currency == "SEK":
        return price_usd * USD_TO_SEK
    elif currency == "NOK":
        return price_usd * USD_TO_NOK
    elif currency == "DKK":
        return price_usd * USD_TO_DKK
    return price_usd  # Standard: USD

# Lägg till konverterad pris-kolumn i datan
df["price"] = df["price_usd"].apply(lambda x: convert_price(x, currency))
df["currency"] = currency

# 2. Visa prisförändringar
df["price_change"] = df["price"].pct_change() * 100  # Prisförändring i %
st.metric("Prisförändring (%)", f"{df['price_change'].iloc[-1]:.2f}%")

st.markdown("## Senaste data")
st.dataframe(df[["coin", "price", "currency", "updated", "timestamp"]].head())




# Skapa dropdown för att välja tidsintervall
timeframe = st.selectbox("Välj tidsintervall:", ["1 timme", "3 timmar", "1 vecka", "1 månad"])
# Filtrera data baserat på valt tidsintervall
if timeframe == "1 timme":
    df_filtered = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(hours=1)]
elif timeframe == "3 timmar":
    df_filtered = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(hours=3)]
elif timeframe == "1 vecka":
    df_filtered = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(weeks=1)]
elif timeframe == "1 månad":
    df_filtered = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(weeks=4)]

# Visa linjediagram över prisförändringar
st.line_chart(df_filtered.set_index("timestamp")["price"])





