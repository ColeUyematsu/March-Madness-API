from pymongo import MongoClient

client = MongoClient("mongodb+srv://cjuyematsu:marchmadness!@marchmadnessdb.ym7yf.mongodb.net/?retryWrites=true&w=majority&appName=MarchMadnessDB")

# Select the database
db = client["MarchMadnessDB"]

# Test connection
print("Connected to MongoDB!")

# List collections
print("Collections:", db.list_collection_names())