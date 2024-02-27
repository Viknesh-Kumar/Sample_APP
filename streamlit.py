import streamlit as st
import pandas as pd
from py3dbp import Packer, Bin, Item
import plotly.graph_objects as go
import time

# Assuming 'DATA_1000 1.xlsx' and 'trucks2_1.xlsx' are in the same directory as the script or uploaded by the user

# Upload boxes data
uploaded_boxes_file = st.file_uploader("Choose a file for boxes data", type=['xlsx'])
if uploaded_boxes_file is not None:
    boxes_df = pd.read_excel(uploaded_boxes_file)
else:
    st.stop()

# Upload trucks data
uploaded_trucks_file = st.file_uploader("Choose a file for trucks data", type=['xlsx'])
if uploaded_trucks_file is not None:
    container_df = pd.read_excel(uploaded_trucks_file)
else:
    st.stop()

selected_df = boxes_df[['Box_ID', 'Box_Type', 'Box_Length', 'Box_Width', 'Box_Height', 'Box_Capcity']].copy()
selected_df.columns = ['Item_Id', 'name', 'length', 'width', 'height', 'weight']

# Process bins
pbins = {
    name: {
        'n': group['name'].count(),
        's': [group['length'].iloc[0], group['width'].iloc[0], group['height'].iloc[0], group['weight'].iloc[0]]
    }
    for name, group in selected_df.groupby('name')
}

 
# Example data for a single box in 3D space

 
# Define which vertices to connect to create the box
def vertices(xmin=0, ymin=0, zmin=0, xmax=1, ymax=1, zmax=1):
    return {
        "x": [xmin, xmin, xmax, xmax, xmin, xmin, xmax, xmax],
        "y": [ymin, ymax, ymax, ymin, ymin, ymax, ymax, ymin],
        "z": [zmin, zmin, zmin, zmin, zmax, zmax, zmax, zmax],
        "i": [7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
        "j": [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        "k": [0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 2],
 
fig = go.Figure(data=[go.Mesh3d(
    x=[v[0] for v in vertices],
    y=[v[1] for v in vertices],
    z=[v[2] for v in vertices],
    i=[mesh3d_indices[i] for i in range(0, len(mesh3d_indices), 4)],
    j=[mesh3d_indices[i+1] for i in range(0, len(mesh3d_indices), 4)],
    k=[mesh3d_indices[i+2] for i in range(0, len(mesh3d_indices), 4)],
    opacity=0.5,
)])
 
fig.show()

containers = container_df[['Truck_Length(Inch)', 'Truck_Width(Inch)', 'Truck_Height(Inch)']].values.tolist()
available_trucks = ["Truck-" + str(i + 1) for i in range(len(containers))]

# Streamlit selection box for trucks
selected_truck = st.selectbox('Select Truck:', available_trucks)

# Function to pack items
def pack_items(containers, pbins):
    packed_data = []
    packer = Packer()
    for i, container in enumerate(containers):
        container_dims = [float(dim) for dim in container]
        packer.add_bin(Bin("Truck-" + str(i + 1), *container_dims, 18000.0))

    for name, cfg in pbins.items():
        for i in range(cfg["n"]):
            item_dims = [float(dim) for dim in cfg["s"]]
            packer.add_item(Item(f"{name}_{i}", *item_dims))

    packer.pack(bigger_first=True, distribute_items=True, number_of_decimals=3)
    return packer

packer = pack_items(containers, pbins)

# Plot function
def plot_for_truck(selected_truck, packer):
    packed_data = []
    for bin in packer.bins:
        if bin.name == selected_truck:
            for item in bin.items:
                packed_data.append(item)

    if not packed_data:
        st.write("No data to display for selected truck.")
        return

    fig = go.Figure()
    for item in packed_data:
        pos = item.position
        dim = item.get_dimension()
        fig.add_trace(go.Mesh3d(
            x=[pos[0], pos[0] + dim[0]],
            y=[pos[1], pos[1] + dim[1]],
            z=[pos[2], pos[2] + dim[2]],
            name=item.name,
            opacity=1
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Length',
            yaxis_title='Width',
            zaxis_title='Height'
        ),
        width=700,
        margin=dict(r=20, l=10, b=10, t=10)
    )
    st.plotly_chart(fig)

if st.button('Show Packing for Selected Truck'):
    plot_for_truck(selected_truck, packer)