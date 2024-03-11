import streamlit as st
import pandas as pd
from py3dbp import Packer, Bin, Item
import pythreejs as p3

def prepare_visualization_data(packed_df, containers):
    boxes_data = []
    for _, row in packed_df.iterrows():
        boxes_data.append({
            'name': row['Item_Id'],
            'width': row['width'], 
            'height': row['height'], 
            'depth': row['length'], 
            'x': row['x'],
            'y': row['y'],
            'z': row['z']
        })

    container_data = {
        'name': selected_truck,
        'width': containers[available_trucks.index(selected_truck)][0],
        'height': containers[available_trucks.index(selected_truck)][1],
        'depth': containers[available_trucks.index(selected_truck)][2],
        'x': 0,
        'y': 0,
        'z': 0
    }

    return boxes_data, container_data
def visualize_packing(boxes_data, container_data):
    # Create boxes
    boxes = [
        p3.BoxGeometry(width=box['width'], height=box['height'], depth=box['depth'])
        for box in boxes_data
    ]

    box_materials = [p3.MeshLambertMaterial(color=f'#{randint(0, 0xffffff):06x}') for _ in boxes_data]
    box_meshes = [p3.Mesh(geometry, material) for geometry, material in zip(boxes, box_materials)]

    # Position boxes
    for box_mesh, box in zip(box_meshes, boxes_data):
        box_mesh.position.set(box['x'], box['y'], box['z'])

    # Create container (with some transparency)
    container_geometry = p3.BoxGeometry(
        width=container_data['width'], 
        height=container_data['height'], 
        depth=container_data['depth']
    )
    container_material = p3.MeshLambertMaterial(opacity=0.3, transparent=True)
    container_mesh = p3.Mesh(container_geometry, container_material)

    # Setup scene, camera, renderer
    scene = p3.Scene(children=[*box_meshes, container_mesh])
    camera = p3.PerspectiveCamera(position=[50, 50, 50], up=[0, 1, 0])
    renderer = p3.Renderer(camera=camera, scene=scene)

    return renderer

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

# Display the DataFrame 
st.dataframe(packed_df)

# ... (Your imports and existing code) ...
print(packed_df.head())  # Print a sample of your DataFrame
print(packed_df.columns)  # Print the column names
print(packed_df.index)    # Print the index type

# ... (Your code up to the part where packed_df is generated) ...

# Prepare data for visualization 
boxes_data, container_data = prepare_visualization_data(packed_df, containers) 

# Create the visualization
renderer = visualize_packing(boxes_data, container_data)

# Display in Streamlit
st.pythreejs(renderer)
