import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import time
from constants import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
import matplotlib.pyplot as plt


# Växlingskurser
USD_TO_SEK = 10.7
USD_TO_NOK = 11
USD_TO_DKK = 6.9

# Anslut till databasen
connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(connection_string)

# Hämta de senaste 5 XRP-priserna från databasen, sorterat efter timestamp DESC
query = 'SELECT coin, price_usd, updated, timestamp FROM "XRP" ORDER BY timestamp DESC LIMIT 5;'

with engine.connect() as connect:
    df = pd.read_sql(query, connect)

# columns show item next to each other instead of stacking
col1, col2 = st.columns(2)

# Added online xrp logo & Name
with col1:
    st.image("https://cryptologos.cc/logos/xrp-xrp-logo.png", width=150)
with col2:
    st.markdown("# XRP Coin Data")

# Skapa dropdown för val av valuta
currency = st.selectbox("Välj en valuta:", ["USD", "SEK", "NOK", "DKK"])


# Funktion för att konvertera priser till valutan användaren valt
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

# Visa senaste data
st.markdown("## Latest data")
st.dataframe(df[["coin", "price", "currency", "updated", "timestamp"]])


# Funktion för att beräkna prisförändring
def calculate_price_change(df, minutes):
    df_filtered = df[
        df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(minutes=minutes)
    ]
    if len(df_filtered) > 1:
        return (
            (df_filtered["price"].iloc[-1] - df_filtered["price"].iloc[0])
            / df_filtered["price"].iloc[0]
        ) * 100
    return 0


# Beräkna prisförändringar för olika tidsperioder
price_changes = {
    "1 min": calculate_price_change(df, 1),
    "5 min": calculate_price_change(df, 5),
    "10 min": calculate_price_change(df, 10),
    "30 min": calculate_price_change(df, 30),
    "60 min": calculate_price_change(df, 60),
}

# Visa prisförändringar
st.markdown("### Price changes")
for period, change in price_changes.items():
    direction = "↗" if change >= 0 else "↘"
    st.metric(f"{period}", f"{direction} {change:.2f}%")

# GRAPH

# Data för prisförändringar
periods = list(price_changes.keys())
changes = list(price_changes.values())

# Skapa ett stapeldiagram
plt.figure(figsize=(10, 6))
bar_width = 0.5

plt.bar(
    periods,
    changes,
    color=["green" if change >= 0 else "red" for change in changes],
    width=bar_width,
)


# Lägg till etiketter och titel
plt.xlabel("Time period", fontsize=14)
plt.ylabel("Price changes (%)", fontsize=14)
plt.title("Price changes for different time periods", fontsize=20)
plt.axhline(0, color="black", linewidth=1)  # Lägg till en horisontell linje vid y=0

# Grid for readability
plt.grid(axis="y", linestyle="--", alpha=0.6)


# Visa diagrammet
st.pyplot(plt)

time.sleep(30)
st.rerun()
