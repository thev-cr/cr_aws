# import pandas as pd
#
#
# def add_university_ratings(student_profiles_path, university_ratings_path):
#     try:
#         # Load the student profiles from the Excel sheet
#         student_profiles = pd.read_excel(student_profiles_path)
#
#         # Load the university ratings from the CSV file
#         university_ratings = pd.read_csv(university_ratings_path)
#
#         # Merge the datasets on the university names
#         # Assuming the university name column in both datasets is titled 'university'
#         merged_data = student_profiles.merge(university_ratings[['university', 'rating']], on='university', how='left')
#
#         # Rename the rating column to 'uni_rating'
#         merged_data.rename(columns={'rating': 'uni_rating'}, inplace=True)
#
#         # Save the updated dataframe back to an Excel file
#         output_path = student_profiles_path.split('.')[0] + '_with_uni_ratings.xlsx'
#         merged_data.to_excel(output_path, index=False)
#
#         return f"University ratings added successfully. File saved as {output_path}."
#     except Exception as e:
#         return f"An error occurred: {e}"
#
#
# # File paths
# student_profiles= '/Users/thev/Desktop/Stack_Desk/CampusRoot/Uni_rec/ML/Model 2.0/Data/total_uni_list_usa.xlsx'  # Update with the actual path to your Excel file
# university_ratings = '/Users/thev/Desktop/Stack_Desk/CampusRoot/Uni_rec/ML/Model 2.0/Data/valid_uni.csv'  # Update with the actual path to your CSV file
#
# # Call the function with the file paths
# result = add_university_ratings(student_profiles, university_ratings)
# print(result)













import json
import pandas as pd

def add_roi_to_universities(json_file_path, excel_file_path):
    # Load and parse the JSON file
    with open(json_file_path, 'r') as json_file:
        universities = json.load(json_file)

    # Load the Excel file
    roi_data = pd.read_excel(excel_file_path)

    # Iterate over the universities and add the ROI
    for university in universities:
        # Find the matching university in the Excel data
        matching_roi = roi_data[roi_data['Institution'] == university['name']]['ROI'].values
        if len(matching_roi) > 0:
            # Add the ROI to the university entry
            university['roi'] = matching_roi[0]
        else:
            # If no match is found, you might want to handle this case, e.g., set a default value or skip
            university['roi'] = None

    # Save the modified data back to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(universities, json_file, indent=4)

    return "ROI added successfully to the JSON file."

# Paths to your files
json_file_path = '/Users/thev/Desktop/Stack_Desk/CampusRoot/Uni_rec/ML/Model 2.0/Data/imaginary.universities2.json'
excel_file_path = '/Users/thev/Desktop/Stack_Desk/CampusRoot/Uni_rec/ML/Model 2.0/Data/mapped_college_roi_ratings2.json.xlsx'

# Call the function with the file paths
result = add_roi_to_universities(json_file_path, excel_file_path)
print(result)
