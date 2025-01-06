import pandas as pd
import numpy as np

# Load the existing CSV file
input_file = 'attack_data.csv'  # Update with your file path
output_file = 'attack_data_updated.csv'  # Update with your desired output file path

# Read the existing CSV file
data = pd.read_csv(input_file)

# Rename the columns as needed
data.rename(columns={'timestamp': 'frame.time_epoch', 'ip': 'ip.src'}, inplace=True)

# Define the new column order
new_column_order = [
    'frame.time_epoch', 
    'packet_size', 
    'ip.src', 
    'ip.dst', 
    'request_rate', 
    '_ws.col.Protocol', 
    'tcp.dstport', 
    'udp.dstport', 
    'label'
]

# Ensure all new columns exist in the DataFrame
for column in new_column_order:
    if column not in data.columns:
        data[column] = np.nan  # Add missing columns with NaN values

# Generate random data for missing columns
# Assuming the following random data generation logic:
for index, row in data.iterrows():
    if pd.isna(row['packet_size']):
        data.at[index, 'packet_size'] = np.random.randint(100, 1500)  # Random packet size between 100 and 1500 bytes
    if pd.isna(row['ip.dst']):
        data.at[index, 'ip.dst'] = f"192.168.0.{np.random.randint(1, 255)}"  # Random destination IP
    if pd.isna(row['request_rate']):
        data.at[index, 'request_rate'] = np.random.randint(1, 100)  # Random request rate between 1 and 100
    if pd.isna(row['_ws.col.Protocol']):
        data.at[index, '_ws.col.Protocol'] = np.random.choice(['TCP', 'UDP', 'ICMP'])  # Random protocol
    if pd.isna(row['tcp.dstport']):
        data.at[index, 'tcp.dstport'] = np.random.randint(1, 65536)  # Random TCP port
    if pd.isna(row['udp.dstport']):
        data.at[index, 'udp.dstport'] = np.random.randint(1, 65536)  # Random UDP port
    if pd.isna(row['label']):
        data.at[index, 'label'] = np.random.choice(['Normal', 'DDOS', 'Port_Scan', 'SYN_Flood', 'ICMP_Flood'])  # Random label

# Reorder the DataFrame to match the new column order
data = data[new_column_order]

# Save the updated DataFrame to a new CSV file
data.to_csv(output_file, index=False)

print(f"Updated CSV saved to {output_file}")