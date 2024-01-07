import os
import base64
import argparse
import requests
import random
import re
import textwrap
import shutil
import datetime
from playsound import playsound

"""
Not my work, taken from https://github.com/oscie57/tiktok-voice
"""

# Constants
API_DOMAINS = [
    "https://api16-normal-c-useast1a.tiktokv.com",
    "https://api16-normal-c-useast1a.tiktokv.com",
    "https://api16-core-c-useast1a.tiktokv.com",
    "https://api16-normal-useast5.us.tiktokv.com",
    "https://api16-core.tiktokv.com",
    "https://api16-core-useast5.us.tiktokv.com",
    "https://api19-core-c-useast1a.tiktokv.com",
    "https://api-core.tiktokv.com",
    "https://api-normal.tiktokv.com",
    "https://api19-normal-c-useast1a.tiktokv.com",
    "https://api16-core-c-alisg.tiktokv.com",
    "https://api16-normal-c-alisg.tiktokv.com",
    "https://api22-core-c-alisg.tiktokv.com",
    "https://api16-normal-c-useast2a.tiktokv.com",
]
API_PATH = "/media/api/text/speech/invoke/"
USER_AGENT = "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; Build/NRD90M;tt-ok/3.12.13.1)"

VOICES = [
    # DISNEY VOICES
    'en_us_ghostface',            # Ghost Face
    'en_us_chewbacca',            # Chewbacca
    'en_us_c3po',                 # C3PO
    'en_us_stitch',               # Stitch
    'en_us_stormtrooper',         # Stormtrooper
    'en_us_rocket',               # Rocket

    # ENGLISH VOICES
    'en_au_001',                  # English AU - Female
    'en_au_002',                  # English AU - Male
    'en_uk_001',                  # English UK - Male 1
    'en_uk_003',                  # English UK - Male 2
    'en_us_001',                  # English US - Female (Int. 1)
    'en_us_002',                  # English US - Female (Int. 2)
    'en_us_006',                  # English US - Male 1
    'en_us_007',                  # English US - Male 2
    'en_us_009',                  # English US - Male 3
    'en_us_010',                  # English US - Male 4

    # EUROPE VOICES
    'fr_001',                     # French - Male 1
    'fr_002',                     # French - Male 2
    'de_001',                     # German - Female
    'de_002',                     # German - Male
    'es_002',                     # Spanish - Male

    # AMERICA VOICES
    'es_mx_002',                  # Spanish MX - Male
    'br_001',                     # Portuguese BR - Female 1
    'br_003',                     # Portuguese BR - Female 2
    'br_004',                     # Portuguese BR - Female 3
    'br_005',                     # Portuguese BR - Male

    # ASIA VOICES
    'id_001',                     # Indonesian - Female
    'jp_001',                     # Japanese - Female 1
    'jp_003',                     # Japanese - Female 2
    'jp_005',                     # Japanese - Female 3
    'jp_006',                     # Japanese - Male
    'kr_002',                     # Korean - Male 1
    'kr_003',                     # Korean - Female
    'kr_004',                     # Korean - Male 2

    # SINGING VOICES
    'en_female_f08_salut_damour',  # Alto
    'en_male_m03_lobby',           # Tenor
    'en_female_f08_warmy_breeze',  # Warmy Breeze
    'en_male_m03_sunshine_soon',   # Sunshine Soon

    # OTHER
    'en_male_narration',           # narrator
    'en_male_funny',               # wacky
    'en_female_emotional',         # peaceful
]

BATCH_DIR = './batch/'

def make_request(session_id, text_speaker, req_text, api_domain):
    req_text = req_text.replace("+", "plus").replace("&", "and")

    headers = {
        'User-Agent': USER_AGENT,
        'Cookie': f'sessionid={session_id}'
    }

    api_url = f"{api_domain}{API_PATH}"

    params = {
        'text_speaker': text_speaker,
        'req_text': req_text,
        'speaker_map_type': 0,
        'aid': 1233
    }

    response = requests.post(api_url, headers=headers, params=params)

    if response.status_code == 200:
        response_data = response.json()
        if "message" in response_data:
            if response_data["message"] == "Couldn't load speech. Try again.":
                raise Exception("Session ID is invalid")
        return response_data
    elif response.status_code == 400:
        raise Exception(f"Bad request. Status code: {response.status_code}")
    elif response.status_code == 401:
        raise Exception(f"Unauthorized. Status code: {response.status_code}")
    elif response.status_code == 403:
        raise Exception(f"Forbidden. Status code: {response.status_code}")
    elif response.status_code == 404:
        raise Exception(f"Not Found. Status code: {response.status_code}")
    elif response.status_code == 500:
        raise Exception(f"Internal server error. Status code: {response.status_code}")
    elif response.status_code == 502:
        raise Exception(f"Bad Gateway. Status code: {response.status_code}")
    elif response.status_code == 503:
        raise Exception(f"Service Unavailable. Status code: {response.status_code}")
    else:
        raise Exception(f"Failed to make a request to domain {api_domain}. Status code: {response.status_code}")

def tts(session_id, text_speaker="en_us_002", req_text="TikTok Text To Speech", filename='voice.mp3', play=False):
    try:
        for index, api_domain in enumerate(API_DOMAINS):
            print(f"Testing domain {index + 1}: {api_domain}")
            try:
                response_data = make_request(session_id, text_speaker, req_text, api_domain)

                if response_data["message"] == "Couldn't load speech. Try again.":
                    print(f"Error: Session ID is invalid for domain {index + 1}")
                    continue

                vstr = response_data["data"]["v_str"]
                msg = response_data["message"]
                scode = response_data["status_code"]
                log = response_data["extra"]["log_id"]
                dur = response_data["data"]["duration"]
                spkr = response_data["data"]["speaker"]

                b64d = base64.b64decode(vstr)

                with open(filename, "wb") as out:
                    out.write(b64d)

                output_data = {
                    "status": msg.capitalize(),
                    "status_code": scode,
                    "duration": dur,
                    "speaker": spkr,
                    "log": log
                }

                print(output_data)

                if play:
                    playsound(filename)
                    os.remove(filename)

                return output_data
            except Exception as e:
                print(f"Error: {e}")

        print("Error: Failed to make a request to all domains")
        exit(1)  # Exit the program if all domains fail
    except Exception as e:
        print(f"Error: {e}")
        exit(1)  # Exit the program if there's an error