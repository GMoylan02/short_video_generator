import PIL
from PIL import Image, ImageFont, ImageDraw
import glob, os

path = r"assets/"

TITLE_CUTOFF = 130
DEFAULT_FONT_SIZE = 18
DEFAULT_WORDS_PER_LINE = 42

# TODO fix issue with text extending past title card, change the placement of the subreddit name or remove it entirely
def create_title_card(subreddit, title):
    font_size = get_font_size(fr'{title}  /r/{subreddit}')
    helvetica = ImageFont.truetype(path + "Helvetica.ttf", font_size)
    with Image.open(path+"title_card_template.png") as title_card:
        draw = ImageDraw.Draw(title_card)
        line_list = split_title(fr'{title}  /r/{subreddit}')
        for i in range(len(line_list)):
            draw.text((20, 70 + i * font_size), line_list[i], (0, 0, 0), font=helvetica)
        title_card.save(path + "title_card.png")


def split_title(title):
    line_list = []
    word_list = title.split(" ")
    running_total = 0
    line = ""
    max_line_length = get_line_length(title)
    for word in word_list:
        if running_total >= max_line_length:
            running_total = 0
            line_list.append(line)
            line = ""
        line += word + " "
        running_total += len(word) + 1
    line_list.append(line)
    return line_list


def get_font_size(title):
    if len(title) > TITLE_CUTOFF:
        return int(18 * 130/len(title))
    else:
        return DEFAULT_FONT_SIZE


def get_line_length(title):
    if len(title) > TITLE_CUTOFF:
        return int(42 * 18/get_font_size(title))
    else:
        return DEFAULT_WORDS_PER_LINE