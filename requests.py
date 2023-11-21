youtube_category_codes = {
    1: 'Film',
    2: 'Autos and Vehicles',
    10: 'Music',
    15: 'Pets and Animals',
    17: 'Sports',
    18: 'Short Movies',
    19: 'Travel and Events',
    20: 'Gaming',
    21: 'Videoblogging',
    22: 'People and Blogs',
    23: 'Comedy',
    24: 'Entertainment',
    25: 'News and Politics',
    26: 'HowTo and Style',
    27: 'Education',
    28: 'Science and Technology',
    29: 'Nonprofits and Activism',
    30: 'Movies',
    31: 'Anime/Animation',
    32: 'Action/Adventure',
    33: 'Classics',
    34: 'Comedy',
    35: 'Documentary',
    36: 'Drama',
    37: 'Family',
    38: 'Foreign',
    39: 'Horror',
    40: 'Sci-Fi/Fantasy',
    41: 'Thriller',
    42: 'Shorts',
    43: 'Shows',
    44: 'Trailers'
}
import re
import os
import sqlite3
import itertools
from googleapiclient.discovery import build
from data_collection import video_ids, ad_ids
# Load environmental variables to protect access keys
from dotenv import load_dotenv
load_dotenv()
MY_YT_KEY = os.getenv('YT_ACCESS_KEY')
# Create the server to access
youtube_service = build('youtube', 'v3', developerKey=MY_YT_KEY)

# No longer just need to access 50 ids, just send whole list to function that will send requests in batches of 50
my_video_ids = video_ids
my_ad_ids = ad_ids

# Initialize a dictionary to store total video durations by category
video_duration_by_category = {category: 0 for category in youtube_category_codes.values()}

# My list of categories
category_list = []

# Function to get unique video ID's and send API request in batches of 50
def process_video_batches(my_video_ids, batch_size=49):
    # Ensure my db is created before processing data
    create_database()
    # Get set of all ids already in db
    processed_video_ids_db = set(get_processed_video_ids_from_db())

    # Iterate through video ID's in batches
    for i in range(0, len(my_video_ids), batch_size):
        # Use itertools to slice through a set (cant get 50 at a time like i can with a list)
        batch = itertools.islice(my_video_ids, i, i+batch_size)
        # Filter out already processed video ID's
        batch = [video_id for video_id in batch if video_id not in processed_video_ids_db]
        # Fetch data and insert into db
        get_channel_stats(youtube_service, batch, youtube_category_codes)

# Function to extract video details
# @params: youtube_service (server to access youtube api), sample_ids (list of ids mapping to youtube videos), 
#          youtube_category_codes (list of codes mapping to category types)
# Return: category_list (list), video_duration_by_category (dictionary of categories mapping to duration times)
def get_channel_stats(youtube_service, batch_ids, youtube_category_codes):
    try:
        request = youtube_service.videos().list(
            # Snippet will contain general details like category name, contentDetails gives me time information
            part='snippet,contentDetails',
            id=','.join(batch_ids)
        )
        response = request.execute()
        data = response.get('items', [])
        for video in data:
            # Extract snippet and contentDetails
            snippet = video['snippet']
            details = video['contentDetails']
            # Youtube sends categoryId back as a string, convert to int before lookup
            categorycode = int(snippet['categoryId'])
            duration = details['duration']
            title = snippet['title']
            if categorycode is not None and categorycode in youtube_category_codes:
                # Store all my categories in my list
                category_name = youtube_category_codes[categorycode]
                category_list.append(category_name)
                if duration is not None:
                    # Convert youtube timestamp to seconds, and store in dictionary mapping categories to times
                    duration_in_seconds = youtube_duration_to_seconds(duration)
                    video_duration_by_category[category_name] += duration_in_seconds
                    # Store data in db
                    insert_video_data(video['id'], title, category_name, duration_in_seconds)
    except Exception as e:
        print("An error occured: ", str(e))


# Function to convert timestamp in youtube data to actual time
# @params: youtube_duration (a timestamp in youtubes format)
# Return: youtube duration converted into total seconds of runtime
def youtube_duration_to_seconds(youtube_duration):
    # Regex to match with youtube timestamp form (PT00M00S)
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', youtube_duration)
    if match:
        # Convert from string to integer, and return total seconds of time
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    # Timestamp not found in details, return 0
    return 0


# Global flag to create sqlite db
database_created = False
#
# Function to create my database to store video information (to limit my api usage)
# Creates table 'video_data' with columns 'video_id', 'title', 'category_name', 'duration_seconds'; Sets Global_Flag to True once created
#
def create_database():
    global database_created
    if not database_created:
        conn = sqlite3.connect('video_data.db')
        cursor = conn.cursor()

        # Create table to store video information
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS video_data (
                            video_id TEXT PRIMARY KEY,
                            title TEXT,
                            category_name TEXT,
                            duration_seconds INTEGER
                        )
                    ''')
        conn.commit()
        conn.close()

        # Set flag to True once db created
        database_created = True

# Function to insert data into db
def insert_video_data(video_id, title, category_name, duration_seconds):
    try:
        # Connect to db
        conn = sqlite3.connect('video_data.db')
        cursor = conn.cursor()
        # Insert data into table
        cursor.execute('''
                   INSERT INTO video_data (video_id, title, category_name, duration_seconds)
                   VALUES (?, ?, ?, ?)
                    ''', (video_id, title, category_name, duration_seconds))
        conn.commit()
    except sqlite3.Error as e:
        print("An error occured while opening inputting data: ", str(e))
    finally:
        # Close the connection whether exception occured or not
        if conn:
            conn.close()


# Helper function to get list of video ids from my db as a check against sending the same requests to youtubes api
def get_processed_video_ids_from_db():
    conn = sqlite3.connect('video_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT DISTINCT video_id FROM video_data')
    process_video_ids = set(row[0] for row in cursor.fetchall())

    conn.close()

    return process_video_ids



# Example Usage
process_video_batches(video_ids)
print(video_duration_by_category)


