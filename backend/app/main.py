# Import necessary modules from FastAPI
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
# Import uvicorn for running the FastAPI application
import uvicorn
# Import os for file and directory operations
import os
# Import OpenCV for image processing
import cv2
# Import numpy for numerical operations
import numpy as np
# Import imutils for image processing utilities
import imutils
# Import fitz (PyMuPDF) for PDF processing
import fitz  # PyMuPDF library for PDF processing
# Import custom functions from extractFromPdf module
from extractFromPdf import process
from addPeriod import add_period_field, format_skills, extract_skills_periods, sum_skills_periods, update_existing_skills
# Print the updated skills for verification (commented out)
# Import CORS middleware from FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Define paths for the MobileNet SSD model
protopath = "MobileNetSSD_deploy.prototxt"
modelpath = "MobileNetSSD_deploy.caffemodel"

# Load the model once
try:
    # Attempt to load the MobileNet SSD model
    detector = cv2.dnn.readNetFromCaffe(prototxt=protopath, caffeModel=modelpath)
    # Define the classes that the model can detect
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
except Exception as e:
    # If model loading fails, set detector to None and print the error
    detector = None
    print(f"Error loading model: {e}")

# Create a FastAPI application instance
app = FastAPI()
# Add CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this based on your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods, adjust as needed
    allow_headers=["*"],  # Allows all headers, adjust as needed
)

# Define a route for the home endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}
# Define a route for CV info extraction
@app.post("/extract_cv_info", response_class=JSONResponse)
async def extract_cv_info(pdf_file: UploadFile = File(...)):
    # Create a temporary directory for storing uploaded files
    temp_dir = "./tmp/"
    os.makedirs(temp_dir, exist_ok=True)

    # Define the path for saving the uploaded PDF
    pdf_path = os.path.join(temp_dir, pdf_file.filename)
    try:
        # Save the uploaded PDF file
        with open(pdf_path, "wb") as f:
            content = await pdf_file.read()
            f.write(content)
        # Check if the object detection model is loaded
        if detector is None:
            raise HTTPException(status_code=500, detail="Object detection model is not loaded.")
        
        # Define the output folder for processed images
        output_folder = 'img/'
        # Process the PDF and extract information
        results = process(pdf_path, output_folder, detector)
        # Add period field to the extracted data
        updated_data = add_period_field(results[0])
        # Format the skills in the extracted data
        updated_data = format_skills(updated_data)
        # Extract skills and their corresponding periods
        skills_periods_list = extract_skills_periods(updated_data)
        # Sum up the skills periods
        summed_skills_list = sum_skills_periods(skills_periods_list, threshold=0.8)
        # Update the existing skills dictionary
        results = update_existing_skills(summed_skills_list, updated_data)

        # Handle different result types
        if isinstance(results, list) and "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
        elif isinstance(results, str):  # In case the result is a message
            return JSONResponse(content={"message": results})
        elif isinstance(results, dict):  # Expected to be a list of images or results
            return JSONResponse(content={"data": results})
        else:
            raise HTTPException(status_code=500, detail="Unexpected result format.")

    except Exception as e:
        # Raise an HTTP exception if any error occurs during processing
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up: remove the temporary PDF file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        # Optionally clean up the temp directory if it's no longer needed
        if os.path.isdir(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)

# Run the FastAPI application using uvicorn if this script is the main entry point
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
