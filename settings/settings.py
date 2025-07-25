import os
import logging
from datetime import datetime
from dotenv import load_dotenv
# from pymongo import MongoClient
# from sshtunnel import SSHTunnelForwarder

# Load environment variables from .env
load_dotenv()

# output filepath for Google News results
GNEWS_OUTPUT_FILE = os.getenv("GNEWS_OUTPUT_FILE")

# Ensure logs directory exists
log_dir = './logs'
os.makedirs(log_dir, exist_ok=True)

# Construct log and output base name
log_file_name = f"gnews_crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Define log file path
log_file_path = os.path.join(log_dir, log_file_name)

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    filename=log_file_path,
    filemode='w', 
    format='[%(asctime)s] [%(levelname)s] %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Google news search base url
GNEWS_BASE_URL = os.getenv("GNEWS_BASE_URL")

# Define the varialbes for mongoDB connection
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")