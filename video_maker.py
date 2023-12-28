from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import pyttsx3
import random
import re
import librosa
import title_card
from bisect import bisect_left
from pathlib import Path

text_speech = pyttsx3.init()
JAPANESE_VOICE = text_speech.getProperty('voices')[3].id
DAVID_VOICE = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
ZERO_WIDTH_SPACE = r"&#x200B;"
asset_path = r'assets\\'


# TODO implement other subs such as confessions, trueoffmychest,
# TODO make it so certain characters dont count towards no_characters such as " / (), currency signs etcetera etc
# TODO make subs more accurate by making each sub longer than 3 words
# TODO use os.join
# Split based on comma, sentence and make long subs go onto next line


class video:
    def __init__(self, title, post_text):
        self.audio_lengths_list = None
        self.audio_length = None
        self.subs = None
        self.formatted_text = None
        self.no_words = None
        self.title = title
        self.post_text = post_text
        self.no_sections = None
        self.section_list = None  # Where section refers to splitting the text by sentence AND comma
        self.video_clip_list = []
        self.audio_starting_points = None

    def create_video(self):
        self.formatted_text = format_text(self.post_text)
        self.formatted_text = self.title + ". " + self.formatted_text
        self.no_words = get_no_words(self.formatted_text)
        self.section_list = re.split(pattern=r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s|,",
                                     string=self.formatted_text)
        self.no_sections = len(self.section_list) + 1  # The +1 is to count the title as a sentence
        # This generates an audio file for each sentence so that the subtitles can be synced to the audio
        self.generate_audio()
        self.audio_length, self.audio_lengths_list, self.audio_starting_points = self.generate_audio_lengths_list()
        self.subs = self.generate_subs()
        # Removes subs for the title, so I can insert the title card
        j = self.subs[0][0][1]
        i = 0
        title_card_length = get_audio_length("clip_audio0.mp3")
        while j < title_card_length:
            j = self.subs[i+1][0][1]
            self.subs[i] = ((0, 0), "")
            i += 1

        # TODO placeholder
        generator = lambda txt: TextClip(txt, font='Tahoma-Bold', fontsize=72, color='white', stroke_color='black',
                                         stroke_width=3)
        subtitles = SubtitlesClip(self.subs, generator)

        # Randomly select some minecraft footage
        footage_link = "https://youtu.be/intRX7BRA90"
        parkour_footage = VideoFileClip(f"parkour{1 if random.randint(1, 2) == 1 else 2}.mp4")
        video_start = random.randint(22, 480)
        video_end = video_start + self.audio_length + 2
        clip = parkour_footage.subclip(video_start, video_end)

        # Loops through all the audio clips and appends each to the corresponding video
        for i in range(len(self.audio_starting_points) - 1):
            video = clip.subclip(self.audio_starting_points[i], self.audio_starting_points[i + 1])
            video = video.set_audio(AudioFileClip(fr"clip_audio{i}.mp3"))
            video.write_videofile(fr"test_video{i}.mp4")
            self.video_clip_list.append(VideoFileClip(f"test_video{i}.mp4"))
        video_clip = self.video_clip_list[0]

        # Concatenate the videos together
        print("Number of words is " + str(self.no_words))
        for i in range(self.no_sections - 3):
            video_clip = concatenate_videoclips([video_clip, self.video_clip_list[i + 1]])
        video_clip = CompositeVideoClip([video_clip, subtitles.set_position(('center', 'center'))])
        title_card_clip = ImageClip(img=asset_path + "title_card.png").set_start(0)\
            .set_duration(title_card_length).set_pos(("center", "center")).resize(height=350, width=350)
        video_clip = CompositeVideoClip([video_clip, title_card_clip])
        video_clip.write_videofile(preset="ultrafast", filename="test_final_video.mp4")
        delete_videos()


    # Generates audio given the post title and text
    def generate_audio(self):
        text_speech.setProperty("voice", DAVID_VOICE)
        text_speech.setProperty('rate', 275)
        for i in range(len(self.section_list)-1):
            text_speech.save_to_file(self.section_list[i], f"clip_audio{i}.mp3")
        text_speech.runAndWait()

    def generate_audio_lengths_list(self):
        audio_length = 0

        audio_lengths_list = []
        audio_starting_points = []
        audio_starting_points.append(0)
        for i in range(self.no_sections-2):  # TODO
            audio_length += get_audio_length(f"clip_audio{i}.mp3")
            audio_lengths_list.append(get_audio_length(f"clip_audio{i}.mp3"))
            audio_starting_points.append(audio_lengths_list[i])
            audio_starting_points[i + 1] += audio_starting_points[i]
        return audio_length, audio_lengths_list, audio_starting_points

    # Create a list of tuples, each tuple containing a tuple of start and end timestamps and the corresponding string
    # TODO Use max chars per line instead of max words,
    # TODO have subs overflow onto next line
    # TOD
    def generate_subs(self):
        subs = [[[0, 0], ""]]
        MAX_CHARS_PER_LINE = 28
        current_time = 0
        which_subtitle = 0
        seconds_per_char = 0
        for i in range(len(self.section_list) - 1):
            which_char_in_section = 0
            try:
                seconds_per_char = self.audio_lengths_list[i] / len(self.section_list[i])
            except Exception as e:
                print(e)
                print(f"Length of audio lengths list is {len(self.audio_lengths_list)}")
                print(f"Length of sentence list is {len(self.section_list)}")
                print(f"Offending post title is {self.title}")
            word_list = self.section_list[i].split(" ")
            if subs[which_subtitle] is None:
                subs.append([[0, 0], ""])
            subs[which_subtitle][0][0] = current_time
            for word in word_list:
                no_chars = len(word)
                if which_char_in_section + no_chars >= MAX_CHARS_PER_LINE:
                    subs[which_subtitle][0][1] = current_time
                    which_subtitle += 1
                    subs.append([[0, 0], ""])
                    subs[which_subtitle][0][0] = current_time
                    which_char_in_section = 0
                subs[which_subtitle][1] += word + " "
                current_time += seconds_per_char * no_chars
                which_char_in_section += no_chars + 1
            subs[which_subtitle][0][1] = current_time
            current_time = take_closest(self.audio_starting_points, current_time)
            which_subtitle += 1
            subs.append([[0, 0], ""])
        return subs

    """
    def generate_subs_old(self):
        subs = [[[0, 0], ""]]
        MAX_WORDS = 3
        MAX_CHARS_PER_LINE = 32
        current_time = 0
        which_subtitle = 0
        for i in range(len(self.sentence_list) - 1):
            try:
                no_commas_in_sentence = self.sentence_list[i].count(",")
                seconds_per_char = self.audio_lengths_list[i] / (len(self.sentence_list[i]) + COMMA_LEN*no_commas_in_sentence)  #count commas as 2 charas
            except Exception as e:
                print(e)
                print(f"Length of audio lengths list is {len(self.audio_lengths_list)}")
                print(f"Length of sentence list is {len(self.sentence_list)}")
                print(f"Offending post title is {self.title}")
            which_word_in_sub = 0
            word_list = self.sentence_list[i].split(" ")
            if subs[which_subtitle] is None:
                subs.append([[0, 0], ""])
            subs[which_subtitle][0][0] = current_time
            for word in word_list:
                if which_word_in_sub >= MAX_WORDS:
                    subs[which_subtitle][0][1] = current_time
                    which_word_in_sub = 0
                    which_subtitle += 1
                    subs.append([[0, 0], ""])
                    subs[which_subtitle][0][0] = current_time
                subs[which_subtitle][1] += word + " "
                no_commas_in_word = word.count(",")
                no_chars = len(word) + COMMA_LEN*no_commas_in_word
                current_time += seconds_per_char * no_chars
                which_word_in_sub += 1
            subs[which_subtitle][0][1] = current_time
            current_time = take_closest(self.audio_starting_points, current_time)
            which_subtitle += 1
            subs.append([[0, 0], ""])
        return subs
        
    """


def get_audio_length(path):
    try:
        length = librosa.get_duration(filename=path)
        return length
    except Exception as e:
        print(e)
        return None


def format_text(post_text):

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
    return formatted_text


def delete_videos():
    # In case there are an unequal number of video and audio files
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