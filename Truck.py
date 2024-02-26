import streamlit as st
import pandas as pd
from py3dbp import Packer, Bin, Item
import plotly.graph_objects as go
import time
 
# Define a function to get vertices for plotly visualization
def vertices(xmin=0, ymin=0, zmin=0, xmax=1, ymax=1, zmax=1):
    return {
        "x": [xmin, xmin, xmax, xmax, xmin, xmin, xmax, xmax],
        "y": [ymin, ymax, ymax, ymin, ymin, ymax, ymax, ymin],
        "z": [zmin, zmin, zmin, zmin, zmax, zmax, zmax, zmax],
        "i": [7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
        "j": [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        "k": [0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 2],
    }
 
# Define a function to convert packer items for plotly visualization
def packer_to_plotly(item):
    colors = ["crimson", "limegreen", "green", "red", "cyan", "magenta", "yellow"]
    color_index = (ord(item.name[0].upper()) - ord('A')) % len(colors)
    ret = vertices(
        *item.position, *[sum(x) for x in zip(item.position, item.get_dimension())]
    )
    ret["name"] = item.name
    ret["color"] = colors[color_index]
    return ret
 
# Loading Data - Assuming an Excel file upload for boxes data
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    boxes_df = pd.read_excel(uploaded_file)
    # Process your data
else:
    st.text("Please upload a file to continue.")
 
# Assume trucks data is fixed or also uploaded
# For demonstration, let's say it's uploaded
uploaded_truck_file = st.file_uploader("Upload truck dimensions file")
if uploaded_truck_file is not None:
    container_df = pd.read_excel(uploaded_truck_file)
    # Extract the container dimensions as a list of lists
    containers = container_df[['Truck_Length(Inch)', 'Truck_Width(Inch)', 'Truck_Height(Inch)']].values.tolist()
else:
    st.text("Please upload the truck dimensions file to continue.")
 
# Assuming the rest of the processing is conditional on the above data being loaded
if uploaded_file is not None and uploaded_truck_file is not None:
    # Preprocessing steps (similar to the original code but adapted for Streamlit)
    # ...
 
    # User selects a truck to visualize
    available_trucks = ["Truck-" + str(i + 1) for i in range(len(containers))]
    selected_truck = st.selectbox('Select Truck:', available_trucks)
 
    # Button to trigger packing and visualization
    if st.button('Pack and Visualize'):
        # Perform packing
        # pack_items function needs to be defined similarly to the original code, adapted for Streamlit
        # pack_items(containers, pbins)
 
        # Visualization (assuming you have a function to visualize for a specific truck)
        # This function needs to be adapted to return a Plotly figure, which can then be displayed
        # fig = plot_for_truck(selected_truck, containers)
        # st.plotly_chart(fig, use_container_width=True)
 
        # Alternativelye.g., `st.selectbox` for dropdowns).
5. **Display Outputs**: Convert any output displays or plots to use Streamlit's display methods (e.g., `st.write` for text, `st.dataframe` for data frames, and `st.plotly_chart` for Plotly graphs).
6. **Run the App**: Once the script is adapted, you can run your Streamlit app using the command `streamlit run your_script_name.py` in your terminal.
 
Below is a complete rewritten version of the provided script, adapted for Streamlit:
 
```python
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
        fig.add_trace(go.Box(
            x=[pos[0], pos[0] + dim[0]],
            y=[pos[1], pos[1] + dim[1]],
            z=[pos[2], pos[2] + dim[2]],
            name=item.name,
            opacity=0.7
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
