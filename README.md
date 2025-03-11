# VLM Dataset Builder

A Streamlit application for building and managing image datasets with custom annotations for Vision-Language Models (VLMs).

## Overview

VLM Dataset Builder makes it easy to:
- Load and navigate through images
- Create and apply custom annotation schemas
- Export annotations in a structured JSON format
- Save both images and annotations in an organized directory structure

## Features

### Image Management
- Load images from a local directory
- Navigate through images with previous/next controls
- View image thumbnails in the dataset preview

### Annotation System
- Create custom annotation fields with different data types:
  - String
  - Integer
  - Float
  - Boolean
  - Array (comma-separated values)
- Apply annotations to images
- Edit existing annotations

### Export Capabilities
- Structured directory output with:
  - `images/` folder containing all annotated images
  - `annotations/` folder containing JSON files for each image
  - `index.json` file mapping images to their annotations
- Automatic saving of annotations when navigating between images

## Usage

1. **Load Images**:
   - Enter the path to your image directory (default: "image_raw")
   - Click "Load Images" to import all images from the directory

2. **Configure Annotation Fields**:
   - Add custom keys with the "Add Key" section
   - Choose appropriate data types for each key
   - Delete unwanted keys with the "Delete" button

3. **Annotate Images**:
   - Navigate through images with the Previous/Next buttons
   - Fill in the annotation form for each image
   - Click "Save Annotation" to save your work

4. **Export Settings**:
   - Specify a directory for exports (default: "vlm_dataset_export")
   - Use "Update Export Directory" to create the directory structure

## Directory Structure

The application creates the following directory structure for exports:

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
└── index.json
```

## Requirements

- Python 3.6+
- Streamlit
- Pandas
- PIL (Pillow)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Example JSON Structure

For an image `example.jpg`, the corresponding annotation file `example.json` might look like:

```json
{
  "caption": "A scenic mountain landscape at sunset",
  "tags": ["mountains", "sunset", "nature"],
  "rating": 4.5,
  "is_featured": true
}
```

## Tips

- For multi-value fields, use the "array" type and enter values as comma-separated items
- Annotations are automatically saved when navigating between images
- Use the dataset preview to quickly review your annotations
