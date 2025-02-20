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
import plotly.graph_objects as go

# Växlingskurser
USD_TO_SEK = 10.7
USD_TO_NOK = 11
USD_TO_DKK = 7

# Connect to the database
connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(connection_string)


# Hämta de senaste XRP-priserna från databasen
#WHERE timestamp >= NOW() - INTERVAL '24 hours'
query = '''SELECT coin, price_usd, updated, timestamp 
FROM "XRP" 
ORDER BY timestamp DESC;'''

with engine.connect() as connect:
    df = pd.read_sql(query, connect)


# columns show item next to each other instead of stacking
col1, col2 = st.columns(2)

# Added online XRP logo & Name
with col1:
    st.image("https://cryptologos.cc/logos/xrp-xrp-logo.png", width=150)
with col2:
    st.markdown("# XRP Coin Data")

# Create a dropdown for selecting currency
currency = st.selectbox("Select a currency:", ["USD", "SEK", "NOK", "DKK"])

# Function to convert prices to the selected currency
def convert_price(price_usd, currency):
    if currency == "SEK":
        return price_usd * USD_TO_SEK
    elif currency == "NOK":
        return price_usd * USD_TO_NOK
    elif currency == "DKK":
        return price_usd * USD_TO_DKK
    return price_usd  # Default: USD

# Add a new column for the converted price
df["price"] = df["price_usd"].apply(lambda x: convert_price(x, currency))
df["currency"] = currency

# Show the latest data
st.markdown("## Latest data")
st.dataframe(df[["coin", "price", "currency", "updated", "timestamp"]])


# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

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

# Calculate price changes for different time periods
price_changes = {
    "5 min": calculate_price_change(df, 10),
    "10 min": calculate_price_change(df, 10),
    "30 min": calculate_price_change(df, 30),
    "60 min": calculate_price_change(df, 60),
}


# Visa prisförändringar i en 2x2 kvadratlayout
st.markdown("### Price Changes")

row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

columns = [row1_col1, row1_col2, row2_col1, row2_col2]

# Display each price change in its respective column
for col, (period, change) in zip(columns, price_changes.items()):
    direction = "↗" if change >= 0 else "↘"
    color = "green" if change >= 0 else "red"
    
    col.markdown(f"<p style='color: {color}; font-size:37px; font-weight:cursive;'>{direction} {change:.2f}%</p>", unsafe_allow_html=True)
    col.write(period)  # Keep period label normal

    
# GRAPH--------------

# Convert timestamp to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Set timestamp as the index to use resampling
df.set_index('timestamp', inplace=True)

# Time intervals in minutes
timeframes = [1, 10, 20, 30, 40, 50, 60]

price_changes = []

# Calculate price changes for each time period
for minutes in timeframes:
    resampled_df = df['price_usd'].resample(f'{minutes}T').last()  # Fetch the last price per time period
    if len(resampled_df) > 1:
        price_change = ((resampled_df.iloc[-1] - resampled_df.iloc[0]) / resampled_df.iloc[0]) * 100
    else:
        price_change = 0
    price_changes.append(price_change)

# Create an interactive graph using Plotly
fig = go.Figure()

# Add line for price changes with colors based on the changes
for i in range(1, len(timeframes)):
    color = 'green' if price_changes[i] >= 0 else 'red'
    fig.add_trace(go.Scatter(
        x=timeframes[i-1:i+1],
        y=price_changes[i-1:i+1],
        mode='lines+markers',
        line=dict(color=color, width=3),
        marker=dict(size=8, color='black', line=dict(width=2)),
        name=f"{timeframes[i-1]}-{timeframes[i]} min"
    ))

# Update layout for interactivity
fig.update_layout(
    title="Price changes for XRP over different time intervals",
    xaxis_title="Time period (minutes)",
    yaxis_title="Price change (%)",
    hovermode="x unified"
)

# Display the graph in Streamlit
st.plotly_chart(fig)

# Rerun after 30 seconds
time.sleep(30)
st.rerun()
