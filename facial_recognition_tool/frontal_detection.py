import cv2
import sys
import os
import numpy as np

def detect_faces(image_path, face_index):
    # Load the pre-trained deep learning face detector
    face_net = cv2.dnn.readNetFromCaffe("deploy.prototxt.txt", "res10_300x300_ssd_iter_140000.caffemodel")

    # Read the input image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    # Get image dimensions
    (h, w) = image.shape[:2]

    # Construct a blob from the image
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

    # Pass the blob through the network and obtain face detections
    face_net.setInput(blob)
    detections = face_net.forward()

    # Create a directory to save the cropped faces if it doesn't already exist
    output_dir = 'frontal_faces'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Loop over the detections
    for i in range(0, detections.shape[2]):
        # Extract the confidence (probability) associated with the detection
        confidence = detections[0, 0, i, 2]

        # Filter out weak detections by ensuring the confidence is greater than the minimum confidence
        if confidence > 0.5:
            # Compute the (x, y)-coordinates of the bounding box for the face
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Ensure the coordinates are within the image dimensions
            startX = max(0, startX)
            startY = max(0, startY)
            endX = min(w, endX)
            endY = min(h, endY)

            # Crop the face from the image
            face = image[startY:endY, startX:endX]

            # Check if the face region is not empty
            if face.size > 0:
                # Save the cropped face to the output directory with incrementing filenames
                face_filename = os.path.join(output_dir, f'face_{face_index}.jpg')
                status = cv2.imwrite(face_filename, face)

                print(f"[INFO] Image {face_filename} written to filesystem: ", status)

                # Increment the face index for the next face
                face_index += 1

def main():
    # Define the directory containing the images
    input_dir = '../originalFrames'

    if not os.path.exists(input_dir):
        print(f"Error: Directory {input_dir} does not exist")
        sys.exit(1)

    # List all files in the directory
    image_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    if not image_files:
        print(f"No images found in directory {input_dir}")
        sys.exit(1)

    # Initialize the face index
    face_index = 1

    # Process each image file in the directory
    for image_file in image_files:
        image_path = os.path.join(input_dir, image_file)

        print(f"[INFO] Processing {image_path}")
        detect_faces(image_path, face_index)

        # Increment the face index for the next image
        face_index += 1

if __name__ == "__main__":
    main()