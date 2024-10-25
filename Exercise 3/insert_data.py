import pandas as pd
import pymongo

# Step 1: Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["myanimelist_db"]

# Step 2: Drop the entire database
client.drop_database("myanimelist_db")
print("Database 'myanimelist_db' has been dropped.")

# Step 3: Read data from CSV
df = pd.read_csv(r'C:\Users\User\anime_app\anime.csv')

# Print the DataFrame columns to verify their names
print("Columns in the DataFrame:", df.columns)

# Step 4: Strip whitespace from column names
df.columns = df.columns.str.strip()

# Step 5: Check if 'Score' column exists
if 'Score' not in df.columns:
    raise KeyError("The 'Score' column is not found in the DataFrame.")

# Step 6: Convert 'Score' to numeric, replacing invalid entries with NaN
df['Score'] = pd.to_numeric(df['Score'], errors='coerce')

# Step 7: Remove records with NaN in 'Score' column
df = df.dropna(subset=['Score'])

# Step 8: Check for valid float conversion for 'Score' and drop invalid records
df = df[df['Score'].apply(lambda x: isinstance(x, (int, float)))]

# Step 9: Convert the 'Score' column to float64
df['Score'] = df['Score'].astype('float64')

# Step 10: Handle 'Episodes' column
if 'Episodes' not in df.columns:
    raise KeyError("The 'Episodes' column is not found in the DataFrame.")

# Convert 'Episodes' to numeric, replacing invalid entries with 0
df['Episodes'] = pd.to_numeric(df['Episodes'], errors='coerce').fillna(0).astype('int64')

# Step 11: Convert NaN values to None for MongoDB compatibility
data = df.where(pd.notnull(df), None).to_dict('records')

# Step 12: Insert the cleaned data into the 'anime' collection
db['anime'].insert_many(data)

print("Data inserted into 'anime' collection after database reset.")
