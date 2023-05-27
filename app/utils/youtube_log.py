import os
from googleapiclient.discovery import build

api_key = os.en
key = 'AIzaSyAzwFF2RI3TJl7OOSyQusmj9UzgUobBFW4'

youtube = build('youtube', 'v3', developerKey=key)

request = youtube.channels().list(
    part='statistics',
    forUsername='schafer5'
   )

response = request.execute()

print(response)