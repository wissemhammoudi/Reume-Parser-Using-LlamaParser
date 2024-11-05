# Import urlparse from urllib.parse for parsing URLs
from urllib.parse import urlparse
# Import PyPDF2 for working with PDF files
import PyPDF2

def classify_link(uri):
    """
    Classifies the given URI based on its domain.

    Args:
        uri (str): The URI to classify.

    Returns:
        str: The classification of the URI (e.g., 'LinkedIn', 'LeetCode', 'GitHub', 'GitLab', 'Medium', 'Stack Overflow', or 'Other').
    """
    # Parse the given URI
    parsed_uri = urlparse(uri)
    # Extract the domain from the parsed URI and convert to lowercase
    domain = parsed_uri.netloc.lower()

    # Classify the domain of the URI
    if 'linkedin' in domain:
        return 'LinkedIn'
    elif 'leetcode' in domain:
        return 'LeetCode'
    elif 'github' in domain:
        return 'GitHub'
    elif 'gitlab' in domain:
        return 'GitLab'
    elif 'medium' in domain:
        return 'Medium'
    elif 'stackoverflow' in domain:
        return 'Stack Overflow'
    else:
        return 'Other'

def extract_links_with_text_from_pdf(pdf_path):
    """
    Extracts links and their associated text from a PDF file and classifies them.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        list: A list of dictionaries containing link text, URI, and type.
    """
    # Initialize an empty list to store link data
    links_data = []

    try:
        # Open the PDF file in binary read mode
        with open(pdf_path, 'rb') as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Iterate through each page in the PDF
            for page_num in range(len(pdf_reader.pages)):
                # Get the current page
                page = pdf_reader.pages[page_num]
                # Extract text from the page (not used in this function, but kept for potential future use)
                page_text = page.extract_text()

                # Check if the page contains annotations
                if '/Annots' in page:
                    # Iterate through each link annotation on the page
                    for link_annotation in page['/Annots']:
                        # Get the link object
                        link_obj = link_annotation.get_object()
                        # Check if the link object contains a URI
                        if '/A' in link_obj and '/URI' in link_obj['/A']:
                            # Extract the URI
                            uri = link_obj['/A']['/URI']
                            # Classify the link
                            link_type = classify_link(uri)

                            # Flag to check if the URI already exists in links_data
                            found = False
                            # Check if URI already exists in links_data
                            for existing_link in links_data:
                                if existing_link['URI'] == uri:
                                    # Update type if necessary
                                    existing_link['Type'] = link_type
                                    found = True
                                    break

                            # If the URI is not found in links_data, add it
                            if not found:
                                links_data.append({
                                    'URI': uri,
                                    'Type': link_type,
                                })

    # Handle file not found error
    except FileNotFoundError:
        print(f"Error: '{pdf_path}' not found.")
    # Handle any other exceptions
    except Exception as e:
        print(f"Error extracting links with text from {pdf_path}: {e}")

    # If no links were found, return a message
    if not links_data:
        return "There are no links"

    # Return the list of link data
    return links_data

