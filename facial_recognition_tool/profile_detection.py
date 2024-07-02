import cv2
import os
import sys

def detect_faces(image_path, output_dir, face_index):
    """
    Detects faces in the input image and saves them as individual files in the output directory.

    Args:
        image_path (str): The path to the input image.
        output_dir (str): The directory where the detected faces will be saved.
        face_index (int): The index to start numbering the detected faces.

    Returns:
        None
    """

    # Convert image to OpenCV object
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    # Convert image object to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load Haar Cascade algorithm
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")


    def detect_faces_internal(image, gray_image, face_index, flip=False):
        """
        Detects faces in the input image and saves them as individual files in the output directory.

        Args:
            image (numpy.ndarray): The input image.
            gray_image (numpy.ndarray): The grayscale version of the input image.
            face_index (int): The index to start numbering the detected faces.
            flip (bool): Whether to flip the image horizontally.

        Returns:
            None
        """

        # List of rectangles (pixel locations) of detected faces
        faces = face_cascade.detectMultiScale(
            gray_image,
            scaleFactor=1.3,
            minNeighbors=3,
            minSize=(30, 30)
        )

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Crop and save each detected face
        for i, (x, y, w, h) in enumerate(faces):
            face = image[y:y+h, x:x+w]
            face_filename = os.path.join(output_dir, f'sFace_{face_index}.jpg')
            status = cv2.imwrite(face_filename, face)
            print(f"[INFO] Image {face_filename} written to filesystem: ", status)

            # Increment the face index for the next face
            face_index += 1

    # Detect faces in the original image
    detect_faces_internal(image, gray, face_index)

    # Flip the image horizontally
    flipped_image = cv2.flip(image, 1)
    flipped_gray = cv2.cvtColor(flipped_image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the flipped image
    detect_faces_internal(flipped_image, flipped_gray, face_index, flip=True)


def process_images(input_dir, output_dir):
    """
    Processes all images in the input directory, detects faces, and saves them in the output directory.

    Args:
        input_dir (str): The directory containing the input images.
        output_dir (str): The directory where the detected faces will be saved.

    Returns:
        None
    """

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
        detect_faces(image_path, output_dir, face_index)
        
        # Increment the face index for the next image
        face_index += 1


if __name__ == "__main__":
    input_dir = '../originalFrames'
    output_dir = 'side_faces'
    
    process_images(input_dir, output_dir)