import os
import json
import glob
import re
from datasets import Dataset, Image
from huggingface_hub import login

# Set the paths
base_dir = "/home/syahvan/Downloads/motor_new/dataset"
annotations_dir = os.path.join(base_dir, "annotations")
images_dir = os.path.join(base_dir, "images")

# Define the instruction that will be the same for all rows
instruction = """Examine the total number of persons wearing a helmet and those without a helmet. The output should be formatted as a JSON instance that conforms to the schema below.

For example, given the schema:  
```json
{"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
```
A well-formatted instance would be:  
```json
{"foo": ["bar", "baz"]}
```
while the object:  
```json
{"properties": {"foo": ["bar", "baz"]}}
```
is not well-formatted.

Here is the required output schema:  
```json
{"properties": {"person-with-helmet": {"title": "Person with Helmet", "description": "Total count of persons wearing a helmet", "type": "integer"}, "person-without-helmet": {"title": "Person without Helmet", "description": "Total count of persons not wearing a helmet", "type": "integer"}}, "required": ["person-with-helmet", "person-without-helmet"]}
```"""

# Get all the JSON files
json_files = glob.glob(os.path.join(annotations_dir, "*.json"))

# Lists to hold the dataset rows
instructions = []
outputs = []
image_paths = []

for json_file in json_files:
    # Extract the base filename without extension
    base_filename = os.path.basename(json_file)
    base_name_without_ext = os.path.splitext(base_filename)[0]
    
    # Construct the image filename
    image_file = os.path.join(images_dir, base_name_without_ext + ".jpg")
    
    # Check if the image file exists
    if os.path.exists(image_file):
        # Read the JSON file
        with open(json_file, 'r') as f:
            json_str = f.read()
            # Remove comments (which are not valid JSON)
            json_str = re.sub(r'//.*', '', json_str)
            json_content = json.loads(json_str)
        
        # Add to the lists
        instructions.append(instruction)
        outputs.append(json.dumps(json_content))  # Convert to JSON string
        image_paths.append(image_file)
    else:
        print(f"Warning: No matching image found for {json_file}")

# Create a dataset
dataset = Dataset.from_dict({
    'instruction': instructions,
    'output': outputs,
    'image': image_paths
})

# Convert the image paths to actual images
dataset = dataset.cast_column('image', Image())

# Split the dataset into train and test sets
dataset_splits = dataset.train_test_split(test_size=0.2, seed=42)
train_dataset = dataset_splits["train"]
test_dataset = dataset_splits["test"]

# Get Huggingface username and dataset name
hf_username = input("Enter your Huggingface username: ")
dataset_name = input("Enter the name for your dataset: ")
repo_id = f"{hf_username}/{dataset_name}"

# Log in to Huggingface Hub
huggingface_token = input("Enter your Huggingface token: ")
login(token=huggingface_token)

# Push the dataset splits to the Huggingface Hub
train_dataset.push_to_hub(repo_id, split="train")
test_dataset.push_to_hub(repo_id, split="test")

print(f"Dataset successfully uploaded to {repo_id} with train split (80%) and test split (20%)")
