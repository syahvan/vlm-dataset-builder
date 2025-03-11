# VLM Dataset Builder

A Streamlit-based tool for creating and managing datasets for Vision-Language Model (VLM) training. This tool helps you annotate images, create structured datasets, and export in formats compatible with Hugging Face and other VLM training pipelines.

## Features

- Load images from local directories
- Define custom annotation schemas with different data types
- Annotate images with structured metadata
- Navigate through image collections
- Maintain separate JSON annotations for each image

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd VLM\ Dataset\ Builder
```

2. Install the required dependencies:
```bash
pip install streamlit pandas pillow pyarrow uuid
```

## Running the Application

Launch the application with:

```bash
streamlit run app.py
```

The application will start and open in your default web browser.

## How to Use

### 1. Load Images

1. In the sidebar, specify the directory containing your images in the "Image Directory Path" field (default: "image_raw")
2. Click "Load Images" to scan the directory for supported image files
3. The app will display how many images were found

### 2. Configure Annotation Keys

1. In the sidebar under "Annotation Keys Configuration," you'll see existing keys
2. To add a new key:
   - Enter a name in the "Key Name" field
   - Select the data type from the dropdown (string, float, integer, boolean, or array)
   - Click "Add Key"
3. To delete a key, click the "Delete" button next to it

### 3. Annotate Images

1. Navigate through images using the "Previous" and "Next" buttons
2. Fill in the form fields for each annotation key
3. Click "Save Annotation" to store the data
4. For array fields, enter comma-separated values

### 4. Export Your Dataset

1. Specify an export directory in the sidebar (default: "vlm_dataset_export")
2. Click "Update Export Directory" to ensure the directory structure exists
3. Enter an instruction text that will apply to all images in the dataset

## Output Structure

The exported dataset includes:

```
vlm_dataset_export/
├── images/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── annotations/
│   ├── image1.json
│   ├── image2.json
│   └── ...
├── index.json
└── dataset.parquet
```

- **images/**: Contains copies of all annotated images
- **annotations/**: Individual JSON files for each image
- **index.json**: Maps images to their annotation files

## Example Workflow

1. Create a directory named "image_raw" and place your images there
2. Launch the application and load images
3. Add custom annotation keys (e.g., "caption", "tags", "category")
4. Navigate through images and provide annotations

## Tips

- You can clear all annotations by clicking "Clear Dataset" and confirming
- The "Example JSON Structure" in the sidebar shows how your annotations will be structured
- Arrays should be entered as comma-separated values (e.g., "item1, item2, item3")
- The instruction text should describe what task you want the VLM to perform with the images

## Requirements

- Python 3.6+
- Streamlit
- Pandas
- PIL/Pillow
- PyArrow
- UUID
