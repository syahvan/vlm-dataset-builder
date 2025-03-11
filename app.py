import streamlit as st
import pandas as pd
import os
from PIL import Image
import json
from datetime import datetime
import uuid
import shutil
import io

# Set page config
st.set_page_config(page_title="VLM Dataset Builder", layout="wide")

# Initialize session state variables if they don't exist
if 'dataset' not in st.session_state:
    st.session_state.dataset = []
if 'annotation_keys' not in st.session_state:
    st.session_state.annotation_keys = {
        "frame_path": {"type": "string", "required": True}
    }
if 'new_key_name' not in st.session_state:
    st.session_state.new_key_name = ""
if 'new_key_type' not in st.session_state:
    st.session_state.new_key_type = "string"
# New session state variables for image navigation
if 'image_files' not in st.session_state:
    st.session_state.image_files = []
if 'current_image_index' not in st.session_state:
    st.session_state.current_image_index = 0
if 'current_values' not in st.session_state:
    st.session_state.current_values = {}
if 'export_dir' not in st.session_state:
    st.session_state.export_dir = "vlm_dataset_export"
    # Create export directory structure
    os.makedirs(os.path.join(st.session_state.export_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(st.session_state.export_dir, "annotations"), exist_ok=True)

# Define functions
def load_images_from_directory(directory="image_raw"):
    """Load all images from the specified directory"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        return []
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    image_files = []
    
    for filename in os.listdir(directory):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_files.append(os.path.join(directory, filename))
    
    return sorted(image_files)

def go_to_next_image():
    """Navigate to next image"""
    save_current_annotation()
    if st.session_state.image_files:
        st.session_state.current_image_index = (st.session_state.current_image_index + 1) % len(st.session_state.image_files)
        load_current_annotation()
        # Force rerun to update the interface with new values
        st.rerun()

def go_to_previous_image():
    """Navigate to previous image"""
    save_current_annotation()
    if st.session_state.image_files:
        st.session_state.current_image_index = (st.session_state.current_image_index - 1) % len(st.session_state.image_files)
        load_current_annotation()
        # Force rerun to update the interface with new values
        st.rerun()

def get_current_image_path():
    """Get the path of the current image"""
    if st.session_state.image_files and 0 <= st.session_state.current_image_index < len(st.session_state.image_files):
        return st.session_state.image_files[st.session_state.current_image_index]
    return None

def save_current_annotation():
    """Save the current annotation to dataset and immediately write JSON file"""
    current_image_path = get_current_image_path()
    if not current_image_path:
        return
    
    # Check if we already have an entry for this image
    existing_entry_idx = None
    for idx, entry in enumerate(st.session_state.dataset):
        if entry.get("frame_path") == current_image_path:
            existing_entry_idx = idx
            break
    
    # Prepare values for save
    values = st.session_state.current_values.copy()
    values["frame_path"] = current_image_path
    
    # Process array fields
    for key, properties in st.session_state.annotation_keys.items():
        if properties["type"] == "array" and key in values and isinstance(values[key], str) and values[key]:
            values[key] = [item.strip() for item in values[key].split(",")]
    
    # Update or create entry
    if existing_entry_idx is not None:
        st.session_state.dataset[existing_entry_idx].update(values)
        entry = st.session_state.dataset[existing_entry_idx]
    else:
        entry_id = str(uuid.uuid4())
        new_entry = {'id': entry_id}
        new_entry.update(values)
        st.session_state.dataset.append(new_entry)
        entry = new_entry
    
    # Immediately save JSON annotation to export directory
    original_filename = os.path.basename(entry["frame_path"])
    base_name = os.path.splitext(original_filename)[0]
    
    # Copy image to export directory if not already there
    image_destination = os.path.join(st.session_state.export_dir, "images", original_filename)
    if not os.path.exists(image_destination):
        shutil.copy2(entry["frame_path"], image_destination)
    
    # Create JSON data
    json_data = {}
    for key in st.session_state.annotation_keys:
        if key != "frame_path" and key != "id" and key in entry:
            json_data[key] = entry[key]
    
    # Write JSON file
    json_path = os.path.join(st.session_state.export_dir, "annotations", f"{base_name}.json")
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    # Update index.json
    update_index_file()

def update_index_file():
    """Update the index.json file with current dataset entries"""
    index_data = []
    for entry in st.session_state.dataset:
        if "frame_path" in entry:
            original_filename = os.path.basename(entry["frame_path"])
            base_name = os.path.splitext(original_filename)[0]
            
            index_entry = {
                "image": f"images/{original_filename}",
                "annotation": f"annotations/{base_name}.json"
            }
            index_data.append(index_entry)
    
    with open(os.path.join(st.session_state.export_dir, "index.json"), 'w') as f:
        json.dump(index_data, f, indent=2)

def load_current_annotation():
    """Load annotation for current image into the form"""
    current_image_path = get_current_image_path()
    if not current_image_path:
        st.session_state.current_values = {}
        return
    
    # Reset current values first to avoid stale data
    st.session_state.current_values = {}
    
    # Find if we have an entry for this image
    for entry in st.session_state.dataset:
        if entry.get("frame_path") == current_image_path:
            # Load values
            st.session_state.current_values = {
                k: v for k, v in entry.items() 
                if k not in ["id", "frame_path"]
            }
            
            # Handle arrays for display
            for key, value in st.session_state.current_values.items():
                if isinstance(value, list):
                    st.session_state.current_values[key] = ", ".join(map(str, value))
            
            return
    
    # No existing entry found - current_values is already empty

def add_entry(values):
    """Add new entry to the dataset with dynamic keys"""
    entry_id = str(uuid.uuid4())
    new_entry = {'id': entry_id}
    
    # Add all the values from the form
    for key in st.session_state.annotation_keys:
        if key in values:
            new_entry[key] = values[key]
        elif st.session_state.annotation_keys[key]["required"]:
            return None, f"Missing required field: {key}"
    
    st.session_state.dataset.append(new_entry)
    return entry_id, None

def delete_entry(idx):
    """Delete entry from dataset and remove the corresponding JSON file"""
    entry = st.session_state.dataset[idx]
    if "frame_path" in entry:
        original_filename = os.path.basename(entry["frame_path"])
        base_name = os.path.splitext(original_filename)[0]
        json_path = os.path.join(st.session_state.export_dir, "annotations", f"{base_name}.json")
        if os.path.exists(json_path):
            os.remove(json_path)
    
    del st.session_state.dataset[idx]
    update_index_file()

def add_key():
    """Add a new key to the schema"""
    new_key = st.session_state.new_key_name.strip()
    
    if not new_key:
        return "Key name cannot be empty"
    
    if new_key in st.session_state.annotation_keys:
        return f"Key '{new_key}' already exists"
    
    st.session_state.annotation_keys[new_key] = {
        "type": st.session_state.new_key_type,
        "required": False
    }
    
    # Reset the input fields
    st.session_state.new_key_name = ""
    return None

def delete_key(key):
    """Delete a key from the schema"""
    if key == "frame_path":
        return f"Cannot delete required key: {key}"
    
    if key in st.session_state.annotation_keys:
        del st.session_state.annotation_keys[key]
        
        # Also remove this key from all dataset entries
        for entry in st.session_state.dataset:
            if key in entry:
                del entry[key]
        
        # Update all JSON files to reflect the change
        for entry in st.session_state.dataset:
            if "frame_path" in entry:
                original_filename = os.path.basename(entry["frame_path"])
                base_name = os.path.splitext(original_filename)[0]
                json_path = os.path.join(st.session_state.export_dir, "annotations", f"{base_name}.json")
                
                json_data = {}
                for k in st.session_state.annotation_keys:
                    if k != "frame_path" and k != "id" and k in entry:
                        json_data[k] = entry[k]
                
                with open(json_path, 'w') as f:
                    json.dump(json_data, f, indent=2)
                
    return None

# Initialize image_raw directory
if not os.path.exists("image_raw"):
    os.makedirs("image_raw", exist_ok=True)

# Try to load from index.json
index_path = os.path.join(st.session_state.export_dir, "index.json")
if os.path.exists(index_path) and ('dataset' not in st.session_state or not st.session_state.dataset):
    try:
        with open(index_path, 'r') as f:
            index_data = json.load(f)
        
        # Process each entry in the index
        for item in index_data:
            # Get paths from index
            image_path = os.path.join(st.session_state.export_dir, item["image"])
            annotation_path = os.path.join(st.session_state.export_dir, item["annotation"])
            
            # Check if both files exist
            if os.path.exists(image_path) and os.path.exists(annotation_path):
                # Get the original filename
                original_filename = os.path.basename(image_path)
                
                # Create a copy in image_raw directory if it doesn't exist
                img_path = os.path.join("image_raw", original_filename)
                if not os.path.exists(img_path):
                    shutil.copy2(image_path, img_path)
                
                # Read annotation data
                with open(annotation_path, 'r') as f:
                    annotation_data = json.load(f)
                
                # Create entry for dataset
                entry_id = str(uuid.uuid4())
                entry = {
                    'id': entry_id,
                    'frame_path': img_path
                }
                entry.update(annotation_data)
                
                # Add to dataset
                st.session_state.dataset.append(entry)
                
                # Add relevant keys to schema if they don't exist
                for key in annotation_data.keys():
                    if key not in st.session_state.annotation_keys:
                        value = annotation_data[key]
                        value_type = type(value)
                        if value_type == list:
                            data_type = "array"
                        elif value_type == bool:
                            data_type = "boolean"
                        elif value_type == int:
                            data_type = "integer" 
                        elif value_type == float:
                            data_type = "float"
                        else:
                            data_type = "string"
                            
                        st.session_state.annotation_keys[key] = {
                            "type": data_type,
                            "required": False
                        }
        
        # Load all images from image_raw
        if not st.session_state.image_files:
            st.session_state.image_files = load_images_from_directory("image_raw")
            
        st.success(f"Loaded {len(st.session_state.dataset)} annotations from previous session")
    except Exception as e:
        st.error(f"Error loading from index.json: {e}")

# Create sidebar
with st.sidebar:
    st.title("VLM Dataset Builder")
    st.markdown("Build datasets for Vision-Language Model training")
    
    # Image folder selection
    st.subheader("Image Directory")
    image_dir = st.text_input("Image Directory Path", "image_raw")
    if st.button("Load Images"):
        st.session_state.image_files = load_images_from_directory(image_dir)
        st.session_state.current_image_index = 0
        load_current_annotation()
        st.rerun()
    
    # Show image count
    st.write(f"Found {len(st.session_state.image_files)} images")
    
    # Key management
    st.subheader("Annotation Keys Configuration")
    
    # Display current keys
    st.write("Current Keys:")
    for key, properties in st.session_state.annotation_keys.items():
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{key}**")
        with col2:
            st.write(f"Type: `{properties['type']}`")
        with col3:
            if key != "frame_path":  # Don't allow deleting frame_path
                if st.button("Delete", key=f"del_{key}"):
                    error = delete_key(key)
                    if error:
                        st.error(error)
                    st.rerun()
    
    # Add new key
    st.subheader("Add New Key")
    st.session_state.new_key_name = st.text_input("Key Name", value=st.session_state.new_key_name)
    st.session_state.new_key_type = st.selectbox(
        "Data Type", 
        options=["string", "float", "integer", "boolean", "array"], 
        index=0
    )
    
    if st.button("Add Key"):
        error = add_key()
        if error:
            st.error(error)
        else:
            st.success(f"Key '{st.session_state.new_key_name}' added")
            st.rerun()
    
    # Dataset summary
    st.subheader("Dataset Summary")
    st.write(f"Total entries: {len(st.session_state.dataset)}")
    
    # Export options
    st.subheader("Export Settings")
    st.session_state.export_dir = st.text_input("Export Directory", st.session_state.export_dir)
    
    # Ensure export directories exist when path changes
    if st.button("Update Export Directory"):
        os.makedirs(os.path.join(st.session_state.export_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(st.session_state.export_dir, "annotations"), exist_ok=True)
        st.success(f"Export directory updated to {st.session_state.export_dir}")
    
    # Clear dataset
    if st.button("Clear Dataset"):
        confirmation = st.checkbox("Confirm delete all annotations", value=False)
        if confirmation:
            st.session_state.dataset = []
            # Remove all JSON files
            annotations_dir = os.path.join(st.session_state.export_dir, "annotations")
            if os.path.exists(annotations_dir):
                for filename in os.listdir(annotations_dir):
                    if filename.endswith('.json') and filename != 'index.json':
                        os.remove(os.path.join(annotations_dir, filename))
            # Reset index file
            with open(os.path.join(st.session_state.export_dir, "index.json"), 'w') as f:
                json.dump([], f, indent=2)
                
            st.success("Dataset cleared")
    
    # Show example JSON structure
    st.subheader("Example JSON Structure")
    example = {}
    for key, properties in st.session_state.annotation_keys.items():
        if key != "frame_path":
            if properties["type"] == "string":
                example[key] = "example text"
            elif properties["type"] == "float":
                example[key] = 42.5
            elif properties["type"] == "integer":
                example[key] = 42
            elif properties["type"] == "boolean":
                example[key] = True
            elif properties["type"] == "array":
                example[key] = ["item1", "item2"]
    
    st.code(json.dumps(example, indent=2), language="json")
    st.write("For an image 'a.jpg', this will be saved as 'a.json'")

# Main content
st.title("VLM Dataset Builder")

# Image navigation and annotation
st.header("Image Annotation")

# Check if we have images loaded
if not st.session_state.image_files:
    st.info("No images loaded. Please load images from the sidebar first.")
else:
    # Display current image status
    current_image_path = get_current_image_path()
    if current_image_path:
        st.write(f"Annotating image {st.session_state.current_image_index + 1} of {len(st.session_state.image_files)}")
        
        # Display the current image
        try:
            image = Image.open(current_image_path)
            st.image(image, width=400, caption=f"Image: {os.path.basename(current_image_path)}")
        except Exception as e:
            st.error(f"Error loading image: {e}")
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button("← Previous"):
                go_to_previous_image()
        with col3:
            if st.button("Next →"):
                go_to_next_image()
        
        # Annotation form
        with st.form(key="annotation_form"):
            # Create form fields for all keys
            for key, properties in st.session_state.annotation_keys.items():
                if key == "frame_path":
                    # This is handled automatically
                    continue
                    
                required_text = " (Required)" if properties["required"] else ""
                field_label = f"{key}{required_text}"
                
                # Set default value from current_values if it exists
                default_value = st.session_state.current_values.get(key, None)
                
                if properties["type"] == "string":
                    st.session_state.current_values[key] = st.text_input(field_label, value=default_value if default_value else "")
                elif properties["type"] == "float":
                    st.session_state.current_values[key] = st.number_input(field_label, value=float(default_value) if default_value is not None else 0.0, step=0.1, format="%.2f")
                elif properties["type"] == "integer":
                    st.session_state.current_values[key] = st.number_input(field_label, value=int(default_value) if default_value is not None else 0, step=1)
                elif properties["type"] == "boolean":
                    st.session_state.current_values[key] = st.checkbox(field_label, value=bool(default_value) if default_value is not None else False)
                elif properties["type"] == "array":
                    st.session_state.current_values[key] = st.text_input(field_label + " (comma-separated items)", value=default_value if default_value else "")
            
            # Submit button
            submit_button = st.form_submit_button("Save Annotation")
        
        # Handle form submission
        if submit_button:
            save_current_annotation()
            st.success("Annotation saved")

# Display dataset
st.header("Dataset Preview")

if len(st.session_state.dataset) > 0:
    for idx, entry in enumerate(st.session_state.dataset):
        with st.container():
            cols = st.columns([1, 3, 1])
            
            # Display image
            with cols[0]:
                try:
                    img = Image.open(entry["frame_path"])
                    filename = os.path.basename(entry["frame_path"])
                    st.image(img, width=150)
                    st.write(f"**Filename:** {filename}")
                except Exception as e:
                    st.error(f"Error loading image: {e}")
            
            # Display metadata
            with cols[1]:
                for key, value in entry.items():
                    if key not in ["id", "frame_path"]:
                        st.write(f"**{key}:** {value}")
            
            # Actions
            with cols[2]:
                if st.button("Delete", key=f"delete_{idx}"):
                    delete_entry(idx)
                    st.rerun()
            
            # Show JSON preview for this entry
            json_preview = {}
            for key, value in entry.items():
                if key not in ["id", "frame_path"]:
                    json_preview[key] = value
            
            filename = os.path.basename(entry["frame_path"])
            base_name = os.path.splitext(filename)[0]
            st.write(f"**{base_name}.json:**")
            st.code(json.dumps(json_preview, indent=2), language="json")
            
            st.divider()
else:
    st.info("No entries yet. Add some images and corresponding values to build your dataset.")

# Directory structure preview
if len(st.session_state.dataset) > 0:
    st.header("Output Directory Structure Preview")
    
    structure = [
        "vlm_dataset_export/",
        "├── images/",
        "│   ├── image1.jpg",
        "│   ├── image2.jpg",
        "│   └── ...",
        "├── annotations/",
        "│   ├── image1.json",
        "│   ├── image2.json",
        "│   └── ...",
        "└── index.json"
    ]
    
    st.code("\n".join(structure), language=None)