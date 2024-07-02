import cv2
import os

def flip_images(input_dir):
    # List all files in the input directory
    image_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    # Initialize a counter
    counter = 1

    # Process each image file in the directory
    for image_file in image_files:
        image_path = os.path.join(input_dir, image_file)

        # Read the input image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image {image_path}")
            continue

        # Flip the image horizontally
        flipped_image = cv2.flip(image, 1)

        # Construct the path for the flipped image
        flipped_image_path = os.path.join(input_dir, f"f_{image_file}")

        # Save the flipped image
        status = cv2.imwrite(flipped_image_path, flipped_image)
        if status:
            print(f"Flipped image saved: {flipped_image_path}")
        else:
            print(f"Error: Failed to save flipped image {flipped_image_path}")

        # Increment the counter
        counter += 1

if __name__ == "__main__":
    target_dir = "side_faces"
    flip_images(target_dir)
