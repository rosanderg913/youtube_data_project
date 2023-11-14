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
from googleapiclient.discovery import build
from data_collection import video_ids, ad_ids


# My api key for yt
yt_api_key = 'AIzaSyDOjxr2IhI5ZEAydA4e99mj8KdgA7zIL9I'
# Create the server to access
youtube_service = build('youtube', 'v3', developerKey=yt_api_key)

# Start by just accessing first 50 members of videos list, and 50 ads
sample_ids = video_ids[0:48]
sample_ads = ad_ids[0:48]

# Initialize a dictionary to store total video durations by category
video_duration_by_category = {category: 0 for category in youtube_category_codes.values()}

# My list of categories
category_list = []

# Function to extract video details
# @params: youtube_service (server to access youtube api), sample_ids (list of ids mapping to youtube videos), 
#          youtube_category_codes (list of codes mapping to category types)
# Return: category_list (list), video_duration_by_category (dictionary of categories mapping to duration times)
def get_channel_stats(youtube_service, sample_ids, youtube_category_codes):
    try:
        request = youtube_service.videos().list(
            # Snippet will contain general details like category name, contentDetails gives me time information
            part='snippet, contentDetails',
            id=sample_ids
            )
        response = request.execute()
        data = response.get('items', [])
        for video in data:
            # Extract snippet, and contentDetails
            snippet = video['snippet']
            # Youtube sends categoryId back as a string, convert to int before lookup
            categorycode = int(snippet['categoryId'])
            duration = video['contentDetails']['duration']
            if categorycode is not None and categorycode in youtube_category_codes:
                # Store all my categories in my list
                category_name = youtube_category_codes[categorycode]
                category_list.append(category_name)
            if duration is not None:
                # Convert youtube timestamp to seconds, and store in dictionary mapping categories to times
                duration_in_seconds = youtube_duration_to_seconds(duration)
                video_duration_by_category[category_name] += duration_in_seconds
    except Exception as e:
        print("An error occured: ", str(e))


# Function to convert timestamp in youtube data to actual time
# @params: youtube_duration (a timestamp in youtubes format)
# Return: youtube duration converted into total seconds of runtime
def youtube_duration_to_seconds(youtube_duration):
    # Regex to match with youtube timestamp form (PT00M00S)
    match = re.match(r'PT(\d+)M(\d+)S', youtube_duration)
    if match:
        # Convert from string to integer, and return total seconds of time
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        total_seconds = minutes * 60 + seconds
        return total_seconds
    # Timestamp not found in details, return 0
    return 0

# Example Usage
get_channel_stats(youtube_service, sample_ids, youtube_category_codes)
print(video_duration_by_category)


