import pandas as pd

# Load the CSV file
input_file = "march_madness.csv"  # Change this to your actual CSV filename
output_file = "flipped_march_madness.csv"  # Output file with reversed rows

# Read the CSV
df = pd.read_csv(input_file)

# Reverse the order of rows
df = df.iloc[::-1].reset_index(drop=True)

# Save to a new CSV file
df.to_csv(output_file, index=False)

print(f"✅ Flipped CSV saved as {output_file}")