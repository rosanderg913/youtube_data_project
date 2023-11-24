import pandas as pd
import seaborn as sbn #importing visualization library
import matplotlib.pyplot as plot


df = pd.read_json('watch-history.json')
video_ids = set()      # To store video IDs     Updated to a set to not allow duplicate id's in my dataset
ad_ids = set()         # To store ad video IDs

for index, row in df.iterrows():
    if (row["title"] != 'Watched a video that has been removed' and row["title"] != 'Answered survey question' and not pd.isna(row["titleUrl"])):   #check if video has been removed and isnt a survey and 'titleurl' is not null
        # Url of video contains video id after 'watch?v='
        url = row["titleUrl"]
        split_url = url.split("watch?v=")
        if len(split_url) > 1:
            id = split_url[1]
            # If the video doesnt have any details (meaning its an ad), or if ad is in the title, add it to my list of ad ids
            if not pd.isna(row["details"]) and any(detail.get("name") == "From Google Ads" for detail in row["details"]):
                ad_ids.add(id)
            else:
                video_ids.add(id)
    else:
        continue

# Example Usage
#print("Video IDS")
#print(video_ids)
#print("AD IDS")
#print(ad_ids)


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
