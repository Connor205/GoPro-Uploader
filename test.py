from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo
from simple_youtube_api.YouTubeVideo import YouTubeVideo

# loggin into the channel
channel = Channel()
channel.login("client_secrets.json", "credentials.storage")

# print(channel.fetch_uploads())
