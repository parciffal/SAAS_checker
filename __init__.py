import pandas as pd

# Load the CSV file
file_name = 'data/input/inputs.csv'  # Replace with your file path
data = pd.read_csv(file_name)

# Calculate the number of rows per file
rows_per_file = len(data) // 10

# Split and save into new files
for i in range(10):
    start_row = i * rows_per_file
    # Handle the last file to include any remaining rows
    end_row = (i + 1) * rows_per_file if i < 9 else len(data)
    split_data = data.iloc[start_row:end_row]
    split_data.to_csv(f'data/input/inputs_{i+1}.csv', index=False)
