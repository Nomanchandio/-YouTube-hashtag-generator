import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = "AIzaSyAVZhXNtFnRkq0Dzx8WZLTd4hxRo-w98q4"

def get_youtube_tags(keyword):
    youtube = build("youtube", "v3", developerKey=API_KEY)

    try:
        search_response = youtube.search().list(
            q=keyword,
            type="video",
            part="id",
            maxResults=5
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

        tags = []
        for video_id in video_ids:
            video_response = youtube.videos().list(
                id=video_id,
                part="snippet"
            ).execute()

            if "tags" in video_response["items"][0]["snippet"]:
                video_tags = video_response["items"][0]["snippet"]["tags"]
                tags.extend(['#' + tag for tag in video_tags])

        return tags
    except HttpError as e:
        error_message = json.loads(e.content)["error"]["message"]
        raise Exception(f"YouTube API error: {error_message}")

def lambda_handler(event, context):
    try:
        if "keyword" not in event:
            raise ValueError("Keyword not found in event")

        tags = get_youtube_tags(event["keyword"])

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Your hashtags are generated!",
                "data": tags
            })
        }
    except ValueError as ve:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f"Bad Request: {str(ve)}",
                "data": []
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Internal Server Error: {str(e)}",
                "data": []
            })
        }

event = {
    "keyword": input("your target keyword: ")
}

print(lambda_handler(event, None))