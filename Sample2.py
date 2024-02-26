import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("Interactive Data Exploration App")

# Data Loading (you can replace this with your method of data loading)
df = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

# Sidebar for User Input
st.sidebar.header("User Input")
selected_column = st.sidebar.selectbox("Select a column", df.columns)
bin_size = st.sidebar.slider("Histogram Bin Size", 1, 10, 5)

# Main App Area
st.subheader(f"Distribution of '{selected_column}'")
fig, ax = plt.subplots()
ax.hist(df[selected_column], bins=bin_size)
st.pyplot(fig)

st.subheader("Data Summary")
st.write(df.describe())
