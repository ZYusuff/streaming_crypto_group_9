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
import matplotlib.pyplot as plt
import time 


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
    

#columns show item next to eachother instead of stacking 
col1, col2 = st.columns(2)

# Added online xrp logo & Name 
with col1:
    st.image("https://cryptologos.cc/logos/xrp-xrp-logo.png", width=150)
with col2:
    st.markdown("# XRP Coin Data")


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


st.markdown("## Latest data")
st.dataframe(df[["coin", "price", "currency", "updated", "timestamp"]].head())



# Funktion för att beräkna prisförändring
def calculate_price_change(df, minutes):
    df_filtered = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(minutes=minutes)]
    if len(df_filtered) > 1:
        return ((df_filtered["price"].iloc[-1] - df_filtered["price"].iloc[0]) / df_filtered["price"].iloc[0]) * 100
    return 0

# Beräkna prisförändringar för olika tidsperioder
price_changes = {
    "1 min": calculate_price_change(df, 1),
    "5 min": calculate_price_change(df, 5),
    "10 min": calculate_price_change(df, 10),
    "30 min": calculate_price_change(df, 30),
}

# Visa prisförändringar
st.markdown("### Price changes")
for period, change in price_changes.items():
    direction = "↗" if change >= 0 else "↘"
    st.metric(f"{period}", f"{direction} {change:.2f}%")


# GRAPH

# Data for price changes
periods = list(price_changes.keys())
changes = list(price_changes.values())

# Create a bar chart
plt.figure(figsize=(10, 6))
plt.bar(periods, changes, color=['green' if change >= 0 else 'red' for change in changes])

# Add labels and title
plt.xlabel('Tidsperiod')
plt.ylabel('Prisförändring (%)')
plt.title('Prisförändringar för olika tidsperioder')
plt.axhline(0, color='black',linewidth=1)  # Add a horizontal line at y=0

# Display the chart
plt.show()



# GRAPH! 
# # Skapa dropdown för att välja tidsintervall
# timeframe = st.selectbox("Välj tidsintervall:", ["1 minut", "3 minuter", "6 minuter", "10 minuter"])

# # Filtrera data baserat på valt tidsintervall
# if timeframe == "1 minut":
#     df_filtered = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(minutes=1)]
# elif timeframe == "3 minuter":
#     df_filtered = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(minutes=3)]
# elif timeframe == "6 minuter":
#     df_filtered = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(minutes=6)]
# elif timeframe == "10 minuter":
#     df_filtered = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(minutes=10)]


time.sleep(30)
st.rerun()

