import streamlit as st
import pandas as pd
from py3dbp import Packer, Bin, Item
import time
import matplotlib.pyplot as plt
start_time = time.time()
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


# ... (Pack items function with slight modifications)
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

    # Collect packing results into a DataFrame
    packed_data = []
    for bin in packer.bins:
        for item in bin.items:
            packed_data.append({
                "Item_Id": item.name,
                "Truck": bin.name,
                "x": item.position[0],
                "y": item.position[1],
                "z": item.position[2] 
            })
    return pd.DataFrame(packed_data) 

# Generate DataFrame with packing assignments
packed_df = pack_items(containers, pbins)
end_time = time.time()
total_runtime = end_time - start_time
st.write(f"Total Runtime (seconds): {total_runtime:.3f}") # Display with 3 decimal places

def visualize_packing_2d(packed_df, truck_length, truck_width):
    fig, ax = plt.subplots()

    # Truck rectangle
    truck_rect = plt.Rectangle((0, 0), truck_length, truck_width, color='gray', alpha=0.6)
    ax.add_patch(truck_rect)

    # Items
    for index, row in packed_df.iterrows():
        item_rect = plt.Rectangle(
            (row['x'], row['y']), 
            row['length'], row['width'], 
            color='lightblue', alpha=0.7
        )
        ax.add_patch(item_rect)
        ax.annotate(row['Item_Id'], xy=(row['x'] + 0.5, row['y'] + 0.5), ha='center', va='center')

    # Labels and limits
    ax.set_xlabel('Truck Length')
    ax.set_ylabel('Truck Width')
    ax.set_xlim(0, truck_length + truck_length * 0.1)  # Add a bit of margin
    ax.set_ylim(0, truck_width + truck_width * 0.1) 

    return fig

# Display the DataFrame 
st.dataframe(packed_df)

# ... (Your existing code to get packed_df, truck, and selected_truck_dimensions)

# Create and display visualization
fig = visualize_packing_2d(packed_df.copy(), *selected_truck_dimensions)  # Copy to avoid side effects

st.pyplot(fig) 


