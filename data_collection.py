import pandas as pd
import seaborn as sbn #importing visualization library
import matplotlib.pyplot as plot


df = pd.read_json('watch-history.json')
video_ids = []      # To store video IDs
ad_ids = []         # To store ad video IDs

for index, row in df.iterrows():
    if (row["title"] != 'Watched a video that has been removed' and row["title"] != 'Answered survey question' and not pd.isna(row["titleUrl"])):   #check if video has been removed and isnt a survey and 'titleurl' is not null
        # Url of video contains video id after 'watch?v='
        url = row["titleUrl"]
        split_url = url.split("watch?v=")
        if len(split_url) > 1:
            id = split_url[1]
            # If the video doesnt have any details (meaning its an ad), or if ad is in the title, add it to my list of ad ids
            if not pd.isna(row["details"]) and any(detail.get("name") == "From Google Ads" for detail in row["details"]):
                ad_ids.append(id)
            else:
                video_ids.append(id)
    else:
        continue

# Example Usage
print("Video IDS")
print(video_ids)
print("AD IDS")
print(ad_ids)



