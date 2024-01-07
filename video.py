from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import random
import re
import librosa
import audio as a

import Constants
#import title_card
from bisect import bisect_left
#from pathlib import Path
import pvleopard
import subtitles as subs

leopard = pvleopard.create(access_key=Constants.PICOVOICE_KEY)
DAVID_VOICE = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
ZERO_WIDTH_SPACE = r"&#x200B;"
asset_path = r'assets/'
footage_path = r'assets\footage/'


def create_video(title, post_text):

    formatted_text = title + '. ' + format_text(post_text)
    full_gameplay = VideoFileClip(get_random_background_video(footage_path))

    audio_path = generate_audio(formatted_text)
    subs_path = generate_subs(audio_path)

    generator = lambda txt: TextClip(txt, font='Tahoma-Bold', fontsize=80, color='white', stroke_color='black',
                                     stroke_width=3)
    subs = SubtitlesClip(subs_path, generator)
    subtitles = SubtitlesClip(subs, generator)
    tts_length = get_audio_length(audio_path)

    video_start = random.randint(22, 430)
    video_end = video_start + tts_length + 2

    background_footage = full_gameplay.subclip(video_start, video_end)

    video = background_footage.set_audio(AudioFileClip(audio_path))
    result = CompositeVideoClip([video, subtitles.set_pos(('center', 'center'))])
    # Comment the next 4 lines of code out for testing
    #title_card_length = get_audio_length("file0.mp3")
    #title_card_clip = ImageClip(img=asset_path + "title_card.png").set_start(0) \
    #    .set_duration(title_card_length).set_pos(("center", "center")).resize(height=350, width=350)
    #result = CompositeVideoClip([result, title_card_clip])
    #
    result.write_videofile(fr"final_video.mp4")


def generate_audio(formatted_text):
    """
    Given the pre-formatted body of the text, turns that text into a
    text-to-speech mp3 file.
    
    :param formatted_text:
    @return: file path to generated audio
    """
    filepath = f'clip_audio.mp3'
    speaker = "en_us_006"
    script_path = string_to_txt(formatted_text)
    req_text = open(script_path, 'r', errors='ignore', encoding='utf-8').read()
    sentence_list = req_text.split('.')
    sentence_list = compress_sentence_list(sentence_list)
    audio_files = []
    for i, sentence in enumerate(sentence_list):
        print(f'sentence {i} is {sentence}')
        a.tts(session_id=Constants.TIKTOK_SESSION, text_speaker=speaker, req_text=sentence, filename=f"file{i}.mp3", play=False)
        audio_files.append(f"file{i}.mp3")
    audios = []
    for i, audio in enumerate(audio_files):
        audios.append(AudioFileClip(audio))
    clips: AudioClip = concatenate_audioclips([audio for audio in audios])
    clips.write_audiofile(filepath)

    return filepath


def string_to_txt(text):
    if text[-1] == '.':
        text = text[:-1]
    with open('script.txt', 'w') as file:
        file.write(text)
    return 'script.txt'


def compress_sentence_list(sentence_list):
    """
    Assuming non-latin characters already removed

    """
    result = []
    result.append(sentence_list[0])
    for sentence in sentence_list[1:]:
        if len(result) == 0:
            result.append(sentence)
        elif len(result[-1] + sentence) < 190 and result[-1] != result[0]:
            result[-1] = result[-1] + sentence
        else:
            result.append(sentence)
    print(f'sentence list is {sentence_list}')
    print(f'result is {result}')
    return result


def generate_subs(audio_path: str):
    """
    Given a path to an mp3 file, generates a subtitle srt file
    :param audio_path:
    :return:
    """
    transcript, words = leopard.process_file(audio_path)

    with open('subs.srt', 'w') as f:
        f.write(subs.to_srt(words))
    return 'subs.srt'


def get_random_background_video(video_directory):
    """
    Given a directory of mp4 files, selects one of them randomly and returns its path

    @param video_directory: filepath to directory containing videos
    @return: file path to the selected video
    """
    return random.choice([x for x in os.listdir(video_directory) if os.path.isfile(os.path.join(video_directory, x))])


def format_text(post_text):
    """
    Given the text of a reddit post, format it according to my needs which include:

    If the post contains some form of TL;DR section, remove that section
    Remove all instances of ZERO_WIDTH_SPACE
    Capitalise all instances of the acronym TIFU

    @param post_text: Body of the Reddit post
    @return: Formatted body of the Reddit post
    """
    formatted_text = ""
    if post_text.upper().__contains__("TL;DR"):
        formatted_text = re.split(pattern="tl;dr", string=post_text, flags=re.IGNORECASE)[0]
    elif post_text.upper().__contains__("TLDR"):
        formatted_text = re.split(pattern="tldr", string=post_text, flags=re.IGNORECASE)[0]
    elif post_text.upper().__contains__("TL DR"):
        formatted_text = re.split(pattern="tl dr", string=post_text, flags=re.IGNORECASE)[0]

    if ZERO_WIDTH_SPACE in formatted_text:
        formatted_text = formatted_text.replace(ZERO_WIDTH_SPACE, '')

    # Doesn't need to be comprehensive, just replace certain common capitalisations of tifu with TIFU
    formatted_text.replace("tifu" or "Tifu" or "tiFU" or "tIFU", "TIFU")

    if len(formatted_text) > 0 and formatted_text[-1] == '.':
        formatted_text = formatted_text[:-1]
    return formatted_text


def delete_videos():
    """
    Deletes intermediary videos (probably unnecessary now)

    :return:
    """
    i = 0
    while os.path.exists(f"clip_audio{i}.mp3"):
        os.remove(f"clip_audio{i}.mp3")
        i += 1
    i = 0
    while os.path.exists(f"test_video{i}.mp4"):
        os.remove(f"test_video{i}.mp4")
        i += 1


def get_no_words(text):
    no_words = len(re.findall(r'\w+', text))
    return no_words


# Not my work, just a utility function
def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before


def get_audio_length(path):
    """
    Given a path to an mp3 file, return its length in seconds

    :param path: File path to the mp3 file
    :return: Length in seconds
    """
    try:
        length = librosa.get_duration(filename=path)
        return length
    except Exception as e:
        print(e)
        return None




