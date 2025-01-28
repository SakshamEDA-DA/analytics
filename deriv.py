import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Page Configuration
st.set_page_config(page_title="Derivatives Trade Analytics", page_icon="📈", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .css-18e3th9 { padding-top: 1rem; }
    .stButton>button { width: 100%; border-radius: 10px; font-size: 16px; font-weight: bold; }
    .stDataFrame { border-radius: 10px; }
    .css-1d391kg { background-color: #f5f7fa; }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Derivatives Trade Analytics Dashboard")

# Upload File
#uploaded_file = st.file_uploader("📂 Upload your trade orders CSV file", type=["csv"])

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://hellfire9109:matchpoint37@saksh.hurcl70.mongodb.net/?retryWrites=true&w=majority&appName=saksh"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
except Exception as e:
    print(e)
db = client["TradeDB"]  # Replace with your database name
collection = db["Trades"]  # Replace with your collection name

# Fetch data from MongoDB
data = list(collection.find({}))  
df = pd.DataFrame(data)

# Drop MongoDB's default `_id` column if not needed
df.drop(columns=["_id"], inplace=True, errors="ignore")
#if uploaded_file is not None:
    #df = pd.read_csv(uploaded_file)
if True:
    # Convert Dates
    df["ClrDate"] = pd.to_datetime(df["ClrDate"], errors="coerce")
    df["Exp"] = pd.to_datetime(df["Exp"], errors="coerce")

    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    selected_exchange = st.sidebar.multiselect("Select Exchange", df["Exc"].unique(), default=df["Exc"].unique())
    selected_product = st.sidebar.multiselect("Select Product Code", df["ProdCode"].unique(), default=df["ProdCode"].unique())

    # Apply Filters
    filtered_df = df[(df["Exc"].isin(selected_exchange)) & (df["ProdCode"].isin(selected_product))]

    # Display Summary in Columns
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", f"{len(filtered_df):,}")
    col2.metric("Unique Clients", f"{filtered_df['Client'].nunique():,}")
    col3.metric("Average Trade Volume", f"{filtered_df['Volume'].mean():,.2f}")
    col4.metric("Total Trade Value", f"${(filtered_df['Price'] * filtered_df['Volume']).sum():,.2f}")

    # Display Filtered Dataset
    st.markdown("### 📋 Filtered Trade Orders Data")
    st.dataframe(filtered_df.style.set_properties(**{"background-color": "#000000", "border-radius": "10px"}))

    # Plots and Analysis
    st.markdown("---")
    st.markdown("## 📈 Trade Insights & Visualizations")

    st.markdown("### 📊 Price & Trade Volume Distribution")

# Create two columns
    col1, col2 = st.columns(2)

    # 📌 Price Distribution
    with col1:
        st.markdown("#### 💰 Price Distribution")
        fig_price = px.histogram(df, x="Price", nbins=50, 
                                title="Price Distribution", 
                                labels={"Price": "Trade Price"},
                                color_discrete_sequence=["#636EFA"])
        st.plotly_chart(fig_price, use_container_width=True)

    # 📌 Trade Volume Distribution
    with col2:
        st.markdown("#### 📈 Trade Volume Distribution")
        fig_volume = px.histogram(df, x="Volume", nbins=50, 
                                title="Trade Volume Distribution", 
                                labels={"Volume": "Trade Volume"},
                                color_discrete_sequence=["#EF553B"])
        st.plotly_chart(fig_volume, use_container_width=True)

    col5,col6=st.columns(2)

    # Exchange-wise Trade Count
    with col5:
        st.markdown("### 🌍 Trades by Exchange")
        fig = px.bar(filtered_df["Exc"].value_counts().reset_index(),
                    labels={"index": "Exchange", "Exc": "Trade Count"}, 
                    title="Trade Count by Exchange", color="Exc", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)
    with col6:
        # Product-wise Trade Distribution
        st.markdown("### 🏷️ Trades by Product Type")
        fig = px.bar(filtered_df["ProdCode"].value_counts().reset_index(),
                    labels={"index": "Product Code", "ProdCode": "Trade Count"}, 
                    title="Trade Count by Product Type", color="ProdCode", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)


    # Trades Over Time
    # Convert to string format
    st.markdown("## 📈 Trades Over Time")

    filtered_df["TradeMonth"] = filtered_df["ClrDate"].dt.to_period("M").astype(str)

    # Group by Trade Month
    trades_over_time = filtered_df.groupby("TradeMonth").size().reset_index(name="Trade Count")

    # Plot using Plotly
    fig = px.line(trades_over_time, x="TradeMonth", y="Trade Count", markers=True, 
                labels={"TradeMonth": "Month", "Trade Count": "Number of Trades"},
                color_discrete_sequence=["#00CC96"])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("*****")

    # Download Processed Data
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Download Processed Data")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(label="Download Filtered CSV", data=csv, file_name="filtered_trades.csv", mime="text/csv")

    st.markdown("### 🏦 Top 10 Clients by Trading Volume")
    top_clients = filtered_df.groupby("Client")["Volume"].sum().nlargest(10).reset_index()
    fig = px.bar(top_clients, x="Client", y="Volume", text="Volume",
                 color="Client",
                color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("*****")
    col3, col4 = st.columns(2)

    # 📌 Buy vs Sell Trades
    with col3:
        st.markdown("### 🔄 Buy vs Sell Trades")
        fig = px.pie(filtered_df, names="BuySell", color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)

    # 📌 Trading Volume Heatmap

