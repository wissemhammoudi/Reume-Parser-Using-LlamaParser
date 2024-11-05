import os
import json
import asyncio
from pathlib import Path
from llama_parse import LlamaParse
import nest_asyncio
from groq import Groq
from deep_translator import GoogleTranslator
from extractLinks import extract_links_with_text_from_pdf
from extractionimage import save_image_and_extract_path
from dotenv import load_dotenv
import logging
from pdfminer.high_level import extract_text
from io import StringIO
import cv2


# Define paths for the MobileNet SSD model
protopath = "MobileNetSSD_deploy.prototxt"
modelpath = "MobileNetSSD_deploy.caffemodel"

# Load the model once
try:
    detector = cv2.dnn.readNetFromCaffe(prototxt=protopath, caffeModel=modelpath)
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
except Exception as e:
    detector = None
    print(f"Error loading model: {e}")

def extract_xml_from_pdf(pdf_path):
    """
    Extracts text from a PDF file and returns it as a string.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    output_string = StringIO()
    try:
        with open(pdf_path, 'rb') as in_file:
            # Create a PDF parser object associated with the file object
            parser = PDFParser(in_file)
            # Create a PDF document object that stores the document structure
            doc = PDFDocument(parser)
            # Create a PDF resource manager object that stores shared resources
            rsrcmgr = PDFResourceManager()
            # Set parameters for analysis
            laparams = LAParams()
            # Create a PDF device object
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            # Create a PDF interpreter object
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            # Process each page contained in the document
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)
                layout = device.get_result()
                for lt_obj in layout:
                    if hasattr(lt_obj, "get_text"):
                        output_string.write(lt_obj.get_text())
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

    return output_string.getvalue()

# Load environment variables from .env file
load_dotenv()

# Initialize API keys from environment variables
API_KEY = os.getenv("GROQ_API_KEY")
API_KEY1 = os.getenv("LlamaParse_API_KEY")

# Apply the nest_asyncio patch to allow nested event loops
nest_asyncio.apply()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Groq client
client = Groq(api_key=API_KEY)

# Function to predict the output based on the given messages
def predict(messages):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0,
            max_tokens=8192,
            top_p=0,
            stream=True,
            stop=None,
        )

        output = ""
        for chunk in completion:
            output += chunk.choices[0].delta.content or ""
        return {"output": output}

    except Exception as e:
        print(f"Error in prediction: {e}")
        return {"output": ""}

# Function to repair and clean a JSON string
def repair_json(json_string, return_objects=False):
    try:
        start_index = json_string.find('{')
        end_index = json_string.rfind('}') + 1
        clean_json_string = json_string[start_index:end_index].strip()
        json_obj = json.loads(clean_json_string)
        return json_obj if return_objects else json.dumps(json_obj)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return {}

# Asynchronous function to extract text from a PDF using LlamaParse
async def extract_text_with_llama(pdf_path, max_retries=2, delay=5):
    parser = LlamaParse(
        api_key=API_KEY1,
        result_type="markdown",
        verbose=True,
        parsing_instruction='Extract the text from the resume and format it in Markdown and the first section let s mardown as personal information',
        do_not_cache=True
    )

    attempt = 0
    while attempt < max_retries:
        try:
            logging.info(f"Processing: {pdf_path} (Attempt {attempt + 1})")
            data = await parser.aload_data(pdf_path)
            if data:
                result = ""  # Initialize result as an empty string
                for t in data:
                    result += t.text + "\n"
                return result
            else:
                raise ValueError("No data returned from LlamaParse.")
        except Exception as e:
            logging.error(f"Error extracting text with LlamaParse: {e}")
            attempt += 1
            if attempt < max_retries:
                logging.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)

    # If all retries fail, use pdfminer
    try:
        logging.info(f"Using pdfminer for extraction: {pdf_path}")
        return extract_text(pdf_path)
    except Exception as e:
        logging.error(f"Error extracting text with pdfminer: {e}")
        return ""
def split_text(text, max_length):
    return [GoogleTranslator(source='auto', target='en').translate(text[i:i + max_length]) for i in range(0, len(text), max_length)]
# Function to process a PDF file and return extracted information
def process(pdf_path, output_folder, detector):
    results = []
    pdf_path = Path(pdf_path)

    try:
        text = asyncio.run(extract_text_with_llama(pdf_path))
        

        if not text:
            raise ValueError(f"Empty text extracted from {pdf_path}")
        
        if len(text) > 4500:
            text=' '.join(split_text(text,4500))
        else: 
            text = GoogleTranslator(source='auto', target='en').translate(text)
        

        messages = [
            {
                "role": "system",
                "content": """
                Extract the following information from the resume text:
                - first and last name
                - contact (email, phone number, location, LinkedIn, GitHub)
                - summary
                - languages
                - skills(can you put all the skills found in th resume in list form)
                - education (institution, duration, degree)
                - internship (duration, technologies, responsibilities, organization name)
                - work experience (duration, technologies, responsibilities, organization name)
                - projects (title, technologies, description, duration)
                - volunteer work (organization name, responsibilities, position)
                - certifications
                - interests and hobbies

                Provide the output as a JSON document with fields 'first and last name', 'contact', 'summary', 'languages', 'skills', 'education', 'internship', 'work experience', 'projects', 'volunteer work', 'certifications', and 'interests and hobbies'. If a field is not present in the text, return an empty string.
                """
            },
            {"role": "user", "content": f"Here is the extracted text: {text}"}
        ]

        response = predict(messages)
        clean_json = repair_json(response["output"], return_objects=True)

        if not isinstance(clean_json, dict):
            print("Error: Response is not a valid JSON object.")
            clean_json = {}

        results.append({
            "first and last name": clean_json.get("first and last name", ""),
            "contact": clean_json.get("contact", {}),
            "summary": clean_json.get("summary", ""),
            "languages": clean_json.get("languages", ""),
            "skills": clean_json.get("skills", ""),
            "education": clean_json.get("education", {}),
            "internship": clean_json.get("internship", {}),
            "work experience": clean_json.get("work experience", {}),
            "projects": clean_json.get("projects", {}),
            "volunteer work": clean_json.get("volunteer work", {}),
            "certifications": clean_json.get("certifications", {}),
            "interests and hobbies": clean_json.get("interests and hobbies", ""),
            "links": extract_links_with_text_from_pdf(pdf_path),
            "image link": save_image_and_extract_path(pdf_path, output_folder, detector)
        })

    except Exception as e:
        print(f"Error processing the PDF file: {e}")

    return results




