# Import necessary libraries
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from google.colab import files

# Step 1: Check if HRDX data is cached
if not os.path.exists("HRDX.xlsx"):
    print("HRDX (training) data not found in cache. Please upload the file:")
    uploaded_hrdx = files.upload()
    hrdx_file_name = list(uploaded_hrdx.keys())[0]
    os.rename(hrdx_file_name, "HRDX.xlsx")  # Cache the file for this session
else:
    print("HRDX (training) data found in cache.")

# Load HRDX data from the cached file
hrdx_data = pd.read_excel("HRDX.xlsx", sheet_name="HRDX")

# Step 2: Upload TodayHR data
print("Please upload the TodayHR (prediction) data file:")
uploaded_todayhr = files.upload()

# Load the uploaded files
todayhr_file_name = list(uploaded_todayhr.keys())[0]
todayhr_data = pd.read_excel(todayhr_file_name)

# Step 3: Load HRDX data from Google Drive
hrdx_data = pd.read_excel(hrdx_file_path, sheet_name="HRDX")

# Step 4: Filter HRDX data for $15-$55 runners
price_filtered_data = hrdx_data[
    (hrdx_data['Price'] >= 15) & (hrdx_data['Price'] <= 55)
].dropna(subset=['P%', 'JH%', 'Rev RTG', 'V4 RTD Pr', 'V4 Rnk', 'Plc'])

# Define thresholds based on analysis
P_THRESHOLD = 70  # Example threshold for P%
JH_THRESHOLD = 75  # Example threshold for JH%
REV_RTG_THRESHOLD = 2.5  # Example threshold for Rev RTG
V4_RTD_PR_THRESHOLD = 10  # Example threshold for V4 RTD Pr
V4_RNK_THRESHOLD = 3  # Example threshold for V4 Rnk

# Step 5: Group data by R-Location and R-Number and apply thresholds
grouped_selections = []

for (location, race_number), group in price_filtered_data.groupby(['R-Location', 'R-Number']):
    # Apply thresholds
    filtered_group = group[
        (group['P%'] >= P_THRESHOLD) &
        (group['JH%'] >= JH_THRESHOLD) &
        (group['Rev RTG'] >= REV_RTG_THRESHOLD) &
        (group['V4 RTD Pr'] <= V4_RTD_PR_THRESHOLD) &
        (group['V4 Rnk'] <= V4_RNK_THRESHOLD)
    ]

    # Calculate predicted accuracy for the group
    if len(filtered_group) > 0:
        filtered_group['Rating'] = (
            (filtered_group['Plc'] <= 3).sum() / len(filtered_group) * 100
        )
        grouped_selections.append(filtered_group)

# Combine all group results into a single DataFrame
final_output = pd.concat(grouped_selections) if grouped_selections else pd.DataFrame()

# Step 6: Sort results by R-Location and R-Number
final_output_sorted = final_output.sort_values(['R-Location', 'R-Number'])[
    ['R-Number', 'R-Location', 'H-Number', 'H-Name', 'Rating']
]

# Step 7: Save and provide the final output
output_file_final = "VPs.csv"
final_output_sorted.to_csv(output_file_final, index=False)

print(f"Final grouped selections saved as '{output_file_final}'. Download the file below:")
files.download(output_file_final)
