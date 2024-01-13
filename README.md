# WIP

#  Short Video Generator

Scrapes topics from Reddit and makes short form Youtube shorts/Tiktok content from it

This is a Python program that curates Reddit posts and generates a `.mp4` file 
with text-to-speech audio, subtitles, and background gameplay footage.

If you are stuck with anything, feel free to shoot me a message on discord at `.faro`

# Usage
To use this, you need Python 3.11+ and all of the required packages installed.
To install the required packages, run ```pip3 install -r requirements.txt```

## Populating Constants.py
Populating Constants.py is a requirement in running this project. 

The following fields are required -

### Reddit Client ID and Secret
These are used in curating Reddit for text-based posts.

Go to https://old.reddit.com/prefs/apps to generate your own Reddit Client ID 
and Reddit Secret.

### Picovoice Key
The Picovoice API uses AI to generate the subtitles and for the video.
Go to https://console.picovoice.ai/ to generate your own Picovoice API key.

### Tiktok Session ID
The Tiktok Session ID is used to generate the text-to-speech audio file.
A guide to get a session ID can be found at 
https://github.com/oscie57/tiktok-voice/wiki/Obtaining-SessionID

## Providing background footage
You also need to provide background footage to be used when generating the videos. The quality 
and aspect ratio of the background footage you provide will be the quality and aspect ratio
of the final product.

Put any `.mp4` files you want to use as background footage into `/assets/footage`





