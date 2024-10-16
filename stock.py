import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import FinanceDataReader as fdr
from pykrx import stock as pkstock
import streamlit as st

# Set global plot style
sns.set_style('whitegrid')

# Streamlit app configuration
st.title('Stock Data Analysis and Visualization')

# Function to convert adjusted price
_OHLC_cols = ['Open', 'High', 'Low', 'Close']

def conv_adj_price(df):
    adj_col = 'Adj Close'
    if adj_col not in df.columns:
        return df
    ndf = df.copy()
    adj_ratio_series = ndf[adj_col] / df['Close']
    ndf[_OHLC_cols] = ndf[_OHLC_cols].multiply(adj_ratio_series, axis=0)
    return ndf

# User input for ticker selection
ticker = st.text_input('Enter stock ticker (e.g., 069500, SPY, AAPL):', 'SPY')

# Fetch data based on user input
if ticker:
    try:
        price_df = fdr.DataReader(ticker)
        adj_price_df = conv_adj_price(price_df)

        # Display dataframe
        st.write(f"Showing data for {ticker}")
        st.dataframe(adj_price_df)

        # Plotting adjusted prices
        st.line_chart(adj_price_df[['Open', 'High', 'Low', 'Close', 'Adj Close']])
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Function to get KOSPI 200 listings
def get_index_listing(index_name, market=None):
    if market is None:
        for _market in ['KOSPI', 'KOSDAQ', 'KRX']:
            res = get_index_listing(index_name, _market)
            if res is not None:
                return res
        return None

    for ticker in pkstock.get_index_ticker_list(market=market):
        name = pkstock.get_index_ticker_name(ticker)
        if name == index_name:
            return pkstock.get_index_portfolio_deposit_file(ticker)
    return None

# Example usage of index listing
index_name = '코스피 200'
if st.button(f'Show listings for {index_name}'):
    listings = get_index_listing(index_name)
    if listings:
        st.write(f"Number of listings in {index_name}: {len(listings)}")
    else:
        st.write(f"No listings found for {index_name}")

# Rolling mean plot example
st.header('Rolling Mean of SPY')
spy_data = fdr.DataReader('SPY')['Adj Close']
mean_sr = spy_data.pct_change(250).rolling(250).mean() * 100

fig, ax = plt.subplots()
ax.plot(mean_sr, color='k', alpha=0.5, label='Rolling Mean')
ax.fill_between(mean_sr.index, 0, mean_sr, where=mean_sr > 0, color='tomato', alpha=0.5)
ax.fill_between(mean_sr.index, 0, mean_sr, where=mean_sr <= 0, color='cornflowerblue', alpha=0.5)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.legend()
st.pyplot(fig)

st.write("This app provides an overview of stock data, including adjusted prices and key metrics.")
