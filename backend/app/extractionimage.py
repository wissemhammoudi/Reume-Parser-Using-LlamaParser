# Import necessary modules
import os  # For file and directory operations
import cv2  # OpenCV for image processing
import numpy as np  # NumPy for numerical operations
import imutils  # For image processing utilities
import fitz  # PyMuPDF library for PDF processing

# Define the classes that the model can detect
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

def detect_person(image_path, detector):
    """
    Detects a person in the given image using the MobileNet SSD model.

    Args:
        image_path (str): Path to the image file.
        detector: The preloaded object detection model.

    Returns:
        int: 1 if a person is detected, 0 otherwise.
    """
    # Check if the detector is loaded
    if detector is None:
        print("Model is not loaded.")
        return 0

    # Read the image using OpenCV
    image = cv2.imread(image_path)
    # Check if the image was successfully read
    if image is None:
        print(f"Error: Image at {image_path} not found or unable to read.")
        return 0

    # Resize the image to a width of 600 pixels
    image = imutils.resize(image, width=600)
    # Get the height and width of the resized image
    (H, W) = image.shape[:2]

    # Create a blob from the image for input to the neural network
    blob = cv2.dnn.blobFromImage(image, 0.007843, (W, H), 127.5)

    # Set the blob as input to the detector
    detector.setInput(blob)
    # Perform forward pass to get detections
    person_detections = detector.forward()

    # Iterate through all detections
    for i in np.arange(0, person_detections.shape[2]):
        # Extract the confidence of the detection
        confidence = person_detections[0, 0, i, 2]
        # Check if the confidence is above the threshold
        if confidence > 0.4:
            # Get the class index of the detection
            idx = int(person_detections[0, 0, i, 1])
            # Check if the detected class is a person
            if CLASSES[idx] == "person":
                print("Person detected.")
                return 1  # Person detected

    # If no person was detected, print a message and return 0
    print("No person detected.")
    return 0  # No person detected

def save_image_and_extract_path(pdf_path, output_folder, detector):
    """
    Extracts images from a PDF file, saves them only if a person is present in the images,
    and deletes other images.

    Args:
        pdf_path (str): Path to the PDF file.
        output_folder (str): Directory to save the extracted images.
        detector: The preloaded object detection model.

    Returns:
        list: List of paths to images with detected persons, or a message if no images are found.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Initialize a list to store paths of images with detected persons
    detected_images = []
    # Get the name of the PDF file without extension
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Iterate through each page in the PDF
    for page_num in range(len(pdf_document)):
        # Load the current page
        page = pdf_document.load_page(page_num)

        # Extract images from the page
        image_list = page.get_images(full=True)
        # If no images found on the page, continue to the next page
        if not image_list:
            print(f"No images found on page {page_num + 1}")
            continue

        # Iterate through each image on the page
        for img_index, image in enumerate(image_list):
            # Get the image reference
            xref = image[0]
            # Extract the image from the PDF
            base_image = pdf_document.extract_image(xref)
            # If image extraction failed, continue to the next image
            if not base_image:
                print(f"Error: Image extraction failed on page {page_num + 1}, image {img_index + 1}.")
                continue

            # Get the image data
            image_bytes = base_image.get("image", None)
            # If no image data found, continue to the next image
            if image_bytes is None:
                print(f"Error: No image data found for page {page_num + 1}, image {img_index + 1}.")
                continue

            # Generate a filename for the image
            image_filename = f"{pdf_name}_page_{page_num + 1}_img_{img_index + 1}.png"
            # Create the full path for the image
            image_path = os.path.join(output_folder, image_filename)

            # Try to save the image
            try:
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                print(f"Image saved: {image_path}")
            except Exception as e:
                print(f"Error: Failed to save image {image_path}. Exception: {e}")
                continue

            # Detect if there's a person in the image
            detected = detect_person(image_path, detector)
            # If a person is detected, add the image path to the list
            if detected:
                detected_images.append(image_path)
            else:
                # If no person is detected, try to delete the image
                try:
                    os.remove(image_path)
                    print(f"Image deleted: {image_path}")
                except Exception as e:
                    print(f"Error: Failed to delete image {image_path}. Exception: {e}")

    # If no images with persons were detected, return a message
    if not detected_images:
        return "There are no images with detected persons."

    # Return the list of paths to images with detected persons
    return detected_images
