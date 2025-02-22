# -*- coding: utf-8 -*-
"""major_project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HqKWiY5Eg7gx1VvU_ajjne-aQflMNMPD
"""

!nvidia-smi

!pip install ultralytics

from ultralytics import YOLO
import os
from IPython.display import display, Image
from IPython import display
display.clear_output()

!pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="iqDWRgNpVBwV38rBvgOX")
project = rf.workspace("projectyolov8-yjbto").project("vehicle_count_prediction")
version = project.version(7)
dataset = version.download("yolov8")

!yolo task=detect mode=train model=yolov8m.pt data=/content/vehicle_count_prediction-7/data.yaml epochs=197 imgsz=244 batch=1

!yolo task=detect mode=predict model=/content/runs/detect/train/weights/best.pt source=/content/frames save_txt=True

import os
import cv2
import matplotlib.pyplot as plt

# Define the class mapping for vehicle types based on your data.yaml
class_names = {
    0: "Auto",
    1: "Car",
    2: "Bus",
    3: "Truck",
    4: "Two_wheeler"
}

# Path to predicted output (where YOLOv8 saved the results)
output_folder = '/content/runs/detect/predict2/labels/'

# Function to count vehicles in a single image
def count_vehicles(image_name):
    # Get corresponding .txt file for the image
    txt_file = os.path.join(output_folder, image_name.replace('.jpg', '.txt').replace('.png', '.txt'))

    if not os.path.exists(txt_file):
        print(f"No .txt file found for {image_name}")
        return {name: 0 for name in class_names.values()}  # Return zero count if no detections

    # Initialize a dictionary to store vehicle counts for each class
    vehicle_counts = {name: 0 for name in class_names.values()}

    # Read the .txt file with predictions
    with open(txt_file, 'r') as f:
        lines = f.readlines()
        if len(lines) == 0:
            print(f"No detections in {txt_file}")
        for line in lines:
            # Parse each detection entry (assuming no confidence value)
            items = line.strip().split()
            class_id = int(items[0])  # First value is class_id

            # Only count vehicles with a valid class_id (0-4)
            if class_id in class_names:
                vehicle_counts[class_names[class_id]] += 1

    return vehicle_counts

# Get list of output images (jpg or png files)
output_images = os.listdir('/content/runs/detect/predict2/')

# Loop over all images and count vehicles for each one
for img_name in output_images:
    if img_name.endswith(('.jpg', '.png')):  # Ensure it's an image file
        image_path = os.path.join('/content/runs/detect/predict2/', img_name)

        # Count the vehicles in the image
        vehicle_count = count_vehicles(img_name)

        # Calculate the total vehicle count
        total_count = sum(vehicle_count.values())

        # Display the results
        print(f"Vehicle count in {img_name}:")
        for vehicle_type, count in vehicle_count.items():
            print(f"{vehicle_type}: {count}")
        print(f"Total Vehicles: {total_count}")

        # Optionally, show the image with vehicle count as the title
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Create the title with counts
        title = (f"Auto: {vehicle_count['Auto']} | Car: {vehicle_count['Car']} | "
                 f"Bus: {vehicle_count['Bus']} | Truck: {vehicle_count['Truck']} | "
                 f"Two_wheeler: {vehicle_count['Two_wheeler']} | Total: {total_count}")

        # Plot the image with the title
        plt.imshow(img_rgb)
        plt.title(title)
        plt.axis('off')
        plt.show()

import cv2
from ultralytics import YOLO
import os

# Path to the folder containing the annotated frames
frames_folder = '/content/frames'  # Folder containing annotated frames

# Path to save the output video
output_video_path = '/content/output.mp4'

# Load the YOLO model (replace 'best.pt' with your trained model if available)
model = YOLO('/content/runs/detect/train3/weights/best.pt')  # Or 'best.pt' if you have custom weights

# Class mapping for vehicle types
class_names = {
    0: "Auto",
    1: "Car",
    2: "Bus",
    3: "Truck",
    4: "Two_wheeler"
}

# Get a list of the annotated frames (make sure the frames are in order)
frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith(('.jpg', '.png'))])

# Check if frames exist in the folder
if not frame_files:
    print("No frames found in the specified folder.")
    exit()

# Get the properties of the first frame (assuming all frames are the same size)
frame = cv2.imread(os.path.join(frames_folder, frame_files[0]))
height, width, _ = frame.shape

# Define the codec and create a VideoWriter for the output video
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Use 'XVID' or another codec
fps = 10  # You can adjust the FPS depending on the video

out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

# Slow down the video by duplicating each frame
slowdown_factor = 10  # Change this to make the video slower. 10 means 10x slower.

# Process each frame and write it to the output video
for frame_file in frame_files:
    frame_path = os.path.join(frames_folder, frame_file)

    # Read the frame
    frame = cv2.imread(frame_path)

    # Run YOLO detection on the frame
    results = model(frame)

    # Initialize vehicle counts
    vehicle_counts = {name: 0 for name in class_names.values()}

    # Process detection results
    for box in results[0].boxes:  # Iterate through detected objects
        cls = int(box.cls[0])  # Class ID
        if cls in class_names:
            vehicle_counts[class_names[cls]] += 1  # Increment count for the detected class

    # Calculate total vehicles
    total_vehicles = sum(vehicle_counts.values())

    # Annotate the frame
    annotated_frame = results[0].plot()  # Annotate frame with bounding boxes and labels

    # Add vehicle count text to the frame
    y_offset = 30  # Starting y position for the text
    cv2.putText(
        annotated_frame, f"Total Vehicles: {total_vehicles}", (10, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA
    )
    y_offset += 30  # Update the y-offset for the next line of text

    for vehicle_type, count in vehicle_counts.items():
        cv2.putText(
            annotated_frame, f"{vehicle_type}: {count}", (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA
        )
        y_offset += 30

    # Slow down the video by duplicating each frame
    for _ in range(slowdown_factor):
        out.write(annotated_frame)

# Release resources
out.release()

print(f"Annotated and slowed down video saved at: {output_video_path}")

import cv2
from ultralytics import YOLO
from google.colab.patches import cv2_imshow  # Import cv2_imshow for displaying images in Colab

# Path to the specific image
image_path = '/content/frames/.jpg'  # Replace with the path to your specific image

# Path to save the annotated image (optional)
output_image_path = '/content/annotated_image.jpg'

# Load the YOLO model (replace 'best.pt' with your trained model if available)
model = YOLO('/content/runs/detect/train3/weights/best.pt')  # Replace with the correct path to your weights file

# Class mapping for vehicle types
class_names = {
    0: "Auto",
    1: "Car",
    2: "Bus",
    3: "Truck",
    4: "Two_wheeler"
}

# Load the specific image
image = cv2.imread(image_path)

# Check if the image is loaded correctly
if image is None:
    print(f"Error: Unable to load the image at {image_path}")
    exit()

# Run YOLO detection on the image
results = model(image)

# Initialize vehicle counts
vehicle_counts = {name: 0 for name in class_names.values()}

# Process detection results
for box in results[0].boxes:  # Iterate through detected objects
    cls = int(box.cls[0])  # Class ID
    if cls in class_names:
        vehicle_counts[class_names[cls]] += 1  # Increment count for the detected class

# Calculate total vehicles
total_vehicles = sum(vehicle_counts.values())

# Annotate the image
annotated_image = results[0].plot()  # Annotate image with bounding boxes and labels

# Add vehicle count text to the image
y_offset = 30  # Starting y position for the text
cv2.putText(
    annotated_image, f"Total Vehicles: {total_vehicles}", (10, y_offset),
    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA
)
y_offset += 30  # Update the y-offset for the next line of text

for vehicle_type, count in vehicle_counts.items():
    cv2.putText(
        annotated_image, f"{vehicle_type}: {count}", (10, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA
    )
    y_offset += 30

# Display the annotated image using cv2_imshow
cv2_imshow(annotated_image)

# Save the annotated image (optional)
cv2.imwrite(output_image_path, annotated_image)
print(f"Annotated image saved at: {output_image_path}")