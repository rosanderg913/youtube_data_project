import sqlite3

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