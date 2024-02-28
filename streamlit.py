import streamlit as st
import pandas as pd
from py3dbp import Packer, Bin, Item
import plotly.graph_objects as go
 
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
 
def vertices(xmin=0, ymin=0, zmin=0, xmax=1, ymax=1, zmax=1):
    return {
        "x": [xmin, xmin, xmax, xmax, xmin, xmin, xmax, xmax],
        "y": [ymin, ymax, ymax, ymin, ymin, ymax, ymax, ymin],
        "z": [zmin, zmin, zmin, zmin, zmax, zmax, zmax, zmax],
        "i": [7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
        "j": [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        "k": [0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 2],
    }
 
containers = container_df[['Truck_Length(Inch)', 'Truck_Width(Inch)', 'Truck_Height(Inch)']].values.tolist()
available_trucks = ["Truck-" + str(i + 1) for i in range(len(containers))]
 
# Streamlit selection box for trucks
selected_truck = st.selectbox('Select Truck:', available_trucks)
 
# Function to pack items
def pack_items(containers, pbins):
    packer = Packer()
    for i, container in enumerate(containers):
        container_dims = [float(dim) for dim in container]
        packer.add_bin(Bin("Truck-" + str(i + 1), *container_dims, 18000.0))
 
    for name, cfg in pbins.items():
        for i in range(cfg["n"]):
            item_dims = [float(dim) for dim in cfg["s"]]
            packer.add_item(Item(f"{name}_{i}", *item_dims))
 
    packer.pack(bigger_first=True, distribute_items=True, number_of_decimals=3)
 
    packed_data = []  # Store the packing results in a local variable
    for i, bin in enumerate(packer.bins):
        for item in bin.items:
            packed_data.append({
                "bin_name": bin.name,
                "bin_index": i,  # Use loop variable i instead of non-existent bin.index
                **{d: v for v, d in zip(item.get_dimension(), list("hwl"))},
                **{d + d: v for v, d in zip(item.position, list("xyz"))}
            })
    return packed_data
 
packed_data = pack_items(containers, pbins)  # Use the returned packed_data for plotting
 
# Plot function
def plot_for_truck(selected_truck, containers, packed_data):
    df = pd.DataFrame(packed_data)
    # Filter by selected truck
    df = df[df['bin_name'].str.contains(selected_truck)]
    # Create a figure for each container (bin)
    for pbin, d in df.groupby("bin_name"):
        fig = go.Figure()
        # Add wireframe for the full truck dimensions (completely transparent)
        truck_dimensions = [float(dim) for dim in containers[int(pbin.split("-")[1]) - 1]]
        truck_outline = vertices(0, 0, 0, *truck_dimensions)
        fig.add_trace(
            go.Mesh3d(
                x=truck_outline["x"],
                y=truck_outline["y"],
                z=truck_outline["z"],
                i=truck_outline["i"],
                j=truck_outline["j"],
                k=truck_outline["k"],
                opacity=0,  # Completely transparent
                color='blue',
                hoverinfo='skip'
            )
        )
        # Plot packed items and grid lines
        xx = []
        yy = []
        zz = []
        for _, r in d.iterrows():
            fig.add_trace(
                go.Mesh3d(r[["x", "y", "z", "i", "j", "k", "name", "color"]].to_dict())
            )
            xx += [r.xx, r.xx + r.h, r.xx + r.h, r.xx, r.xx, None] * 2 + [r.xx] * 5 + [None]
            yy += [r.yy, r.yy, r.yy + r.w, r.yy + r.w, r.yy, None] * 2 + [
                r.yy,
                r.yy + r.w,
                r.yy + r.w,
                r.yy,
                r.yy,
                None,
            ]
            zz += [r.zz] * 5 + [None] + [r.zz + r.l] * 5 + [None] + [r.zz, r.zz, r.zz + r.l, r.zz + r.l, r.zz, None]
        fig.add_trace(
            go.Scatter3d(
                x=xx,
                y=yy,
                z=zz,
                mode="lines",
                line_color="black",
                line_width=2,
                hoverinfo="skip",
            )
        )
        # Configure the figure
        ar = 4
        xr = max(d["x"].max()) - min(d["x"].min())
        aspect_ratio_x = ar
        aspect_ratio_y = ((max(d["y"].max()) - min(d["y"].min())) / xr) * ar
        aspect_ratio_z = ((max(d["z"].max()) - min(d["z"].min())) / xr) * ar
        fig.update_layout(
            title={"text": pbin, "y": 0.9, "x": 0.5, "xanchor": "center", "yanchor": "top"},
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            scene=dict(
                camera=dict(eye=dict(x=2, y=2, z=2)),
                aspectratio=dict(x=aspect_ratio_x, y=aspect_ratio_y, z=aspect_ratio_z),
                aspectmode="manual",
            ),
        )
        # Display the figure in Streamlit
        st.plotly_chart(fig)
 
if st.button('Show Packing for Selected Truck'):
    plot_for_truck(selected_truck, containers, packed_data)
