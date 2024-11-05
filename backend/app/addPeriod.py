# Import necessary libraries
from dateparser.search import search_dates  # For parsing dates from text
from dateutil.relativedelta import relativedelta  # For calculating date differences
from datetime import datetime  # For working with dates and times
import json  # For JSON operations
import re  # For regular expressions
from collections import defaultdict  # For creating dictionaries with default values
from Levenshtein import distance as levenshtein_distance  # For calculating string distances

# Function to add spaces around a specified delimiter in text
def add_spaces_around_delimiter(text, delimiter='-'):
    # Add spaces around the specified delimiter
    # Ensure there is exactly one space before and after the delimiter
    return re.sub(r'(?<! )' + re.escape(delimiter) + r'(?! )', f' {delimiter} ', text)

# Function to get the current date and time
def nowdate():
    return datetime.now()

# Function to calculate the difference between dates in a given text
def calculate_date_difference(text):
    # Search for dates in the text
    dates = search_dates(text)

    # If no dates found, return an error message
    if dates is None:
        return "No valid dates found in the text."

    # If multiple dates found
    if len(dates) > 1:
        # Extract start and end dates
        start_date = dates[0][1]
        end_date = dates[1][1]
        # Calculate the difference between dates
        difference = relativedelta(end_date, start_date)
        # Return the difference as a list of years, months, and days
        return [difference.years , difference.months, difference.days]
    # If only one date found
    elif len(dates) == 1:
        # If "PRESENT" is in the text, calculate difference from the date to now
        if "PRESENT" in text:
            start_date = dates[0][1]
            end_date = nowdate()
            difference = relativedelta(end_date, start_date)
            return [difference.years , difference.months, difference.days]
        else:
            # If no end date provided, return an error message
            return "No end date provided in the text."
    else:
        # If no valid dates found, return an error message
        return "No valid dates found in the text."

# Function to add a 'period' field to data based on 'duration'
def add_period_field(data):
    # Check if the data is a dictionary
    if isinstance(data, dict):
        # Iterate through key-value pairs in the dictionary
        for key, value in data.items():
            # If the value is a list, process each item
            if isinstance(value, list):
                for item in value:
                    # If the item is a dictionary with a 'duration' field
                    if isinstance(item, dict) and 'duration' in item and item['duration']:
                        # Calculate the period and add it to the item
                        period = calculate_date_difference(add_spaces_around_delimiter(item['duration'].upper()))
                        item['period'] = period
            # If the value is a dictionary, recursively process it
            elif isinstance(value, dict):
                add_period_field(value)
    # Return the modified data
    return data

# Function to format skills as a dictionary with 'N/A' values
def format_skills(data):
    # Check if 'skills' is in the data and is a list
    if 'skills' in data and isinstance(data['skills'], list):
        # Convert each skill into a dictionary entry with 'N/A' as its value
        data['skills'] = {skill: 'N/A' for skill in data['skills']}
    # Return the modified data
    return data

# Function to extract skills and their periods from various sections of the data
def extract_skills_periods(data):
    # Initialize a dictionary to store skills and their periods
    skills_periods = {}

    # Helper function to add skills from a section
    def add_skills_from_section(section):
        # If the section is a dictionary
        if isinstance(section, dict):
            # If 'technologies' is in the section and not empty
            if 'technologies' in section and section['technologies']:
                # Handle different types of 'technologies' field
                if isinstance(section['technologies'], str):
                    technologies = [tech.strip() for tech in section['technologies'].split(',')]
                elif isinstance(section['technologies'], list):
                    technologies = section['technologies']
                else:
                    technologies = []  # Handle other unexpected types as needed

                # Get the period for this section
                period = section.get('period', '')
                # Add each technology to the skills_periods dictionary
                for tech in technologies:
                    skills_periods[tech] = period
        # If the section is a list, process each item
        elif isinstance(section, list):
            for item in section:
                add_skills_from_section(item)

    # Extract skills from work experience
    if 'work experience' in data:
        add_skills_from_section(data['work experience'])
    # Extract skills from projects
    if 'projects' in data:
        add_skills_from_section(data['projects'])
    # Extract skills from internship
    if 'internship' in data and isinstance(data['internship'], str) and data['internship']:
        technologies = [tech.strip() for tech in data['internship'].split(',')]
        period = 'N/A'
        for tech in technologies:
            if tech not in skills_periods:
                skills_periods[tech] = period

    # Convert the skills_periods dictionary to a list of tuples
    skills_periods_list = [(skill, period) for skill, period in skills_periods.items()]

    # Return the list of skills and their periods
    return skills_periods_list

# Function to normalize the Levenshtein distance score
def normalize_score(score, max_len):
    return score / max_len if max_len > 0 else 1.0

# Function to sum up periods for similar skills
def sum_skills_periods(skills_periods_list, threshold=0.8):
    # Initialize a defaultdict to store the summed periods
    summed_skills = defaultdict(lambda: [0, 0, 0])
    
    # Create a list to hold the processed skills to avoid duplicate processing
    processed = []

    # Iterate through each skill and its periods
    for skill, periods in skills_periods_list:
        best_match = None
        best_score = float('inf')
        
        # Find the best match among existing skills
        for existing_skill in summed_skills:
            score = levenshtein_distance(skill.lower(), existing_skill.lower())
            max_len = max(len(skill), len(existing_skill))
            normalized_score = normalize_score(score, max_len)
            
            if normalized_score < best_score:
                best_score = normalized_score
                best_match = existing_skill
        
        # If a good match is found, update the existing skill's periods
        if best_match and best_score <= (1 - threshold):  # 1 - threshold to convert threshold to distance
            summed_skills[best_match] = [x + y for x, y in zip(summed_skills[best_match], periods)]
        else:
            # Add the new skill with its period
            summed_skills[skill] = [x + y for x, y in zip(summed_skills[skill], periods)]
    
    # Convert the defaultdict back to a regular list of tuples
    summed_skills_list = [(skill, periods) for skill, periods in summed_skills.items()]

    # Return the list of summed skills and their periods
    return summed_skills_list

# Function to update existing skills or add new ones
def update_existing_skills(skills_list, skills_dict, threshold=0.5):
    
    # Iterate through each skill and its period in the input list
    for skill, period in skills_list:
        # Find the best match in existing_skills
        best_match = None
        best_score = float('inf')
        # Compare the current skill with each existing skill
        for key in skills_dict['skills']:
            score = levenshtein_distance(skill.lower(), key.lower())
            max_len = max(len(skill), len(key))
            normalized_score = score / max_len if max_len > 0 else 1.0
            
            # Update the best match if a better score is found
            if normalized_score < best_score:
                best_score = normalized_score
                best_match = key
        
        # If a good match is found, update the existing skill
        if best_match and best_score <= threshold:
            skills_dict['skills'][best_match] = ', '.join(map(str, period))
        else:
            # If no match found or score is below threshold, add the new skill
            skills_dict['skills'][skill] = ', '.join(map(str, period))
    
    # Return the updated skills dictionary
    return skills_dict

