import sqlite3
from data_collection import youtube_category_codes
import pandas as pd
import seaborn as sbn #importing visualization library
import matplotlib.pyplot as plot
import matplotlib

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

# Initialize a dictionary to store total video durations by category
video_duration_by_category = {category: 0 for category in youtube_category_codes.values()}
def get_video_duration_by_category(video_duration_dictionary):
    try:
        # Connect to db
        conn = sqlite3.connect('video_data.db')
        cursor = conn.cursor()

        # Select video data from db
        cursor.execute('SELECT category_name, duration_seconds FROM video_data')
        rows = cursor.fetchall()

        # Iterate through results and update dictionary
        for row in rows:
            category_name, duration_seconds = row
            video_duration_dictionary[category_name] += duration_seconds
        
    except sqlite3.Error as e:
        print("An error occured while retrieving data from db: ", str(e))
    finally:
        if conn:
            conn.close()
    return video_duration_dictionary


video_duration_by_category = get_video_duration_by_category(video_duration_by_category)

def search_videos_by_keywords(keywords):
    try:
        # Connect to db
        conn = sqlite3.connect('video_data.db')
        cursor = conn.cursor()

        # Prepare the SQL query
        query = '''
            SELECT video_id, title, category_name, duration_seconds
            FROM video_data
            WHERE LOWER(title) LIKE ?
        '''

        # Execute the query for each keyword
        results = []
        for keyword in keywords:
            # Use '%' to match any characters before and after the keyword
            keyword_param = f'%{keyword.lower()}%'
            cursor.execute(query, (keyword_param,))
            rows = cursor.fetchall()
            results.extend(rows)

        return results
    
    except sqlite3.Error as e:
        print("An error occurred while retrieving data from db: ", str(e))
        return []
    finally:
        if conn:
            conn.close()

def get_kobe_data():
    keywords = ['kobe', 'mamba']
    search_results = search_videos_by_keywords(keywords)
    for result in search_results:
        print(result)

def visualize_by_category_time(dic):
    # Create a Pandas DataFrame from the dictionary
    df = pd.DataFrame(list(dic.items()), columns=['Category', 'Duration'])

    # Plot the bar graph
    df.plot(kind='bar', x='Category', y='Duration', legend=False)
    plot.title('Total Video Duration by Category')
    plot.xlabel('Category')
    plot.ylabel('Duration (seconds)')
    plot.show()


visualize_by_category_time(video_duration_by_category)


