"""
Literally just stores any seen ids in a text file
"""


def entry_exists(post_id: str, subreddit: str) -> bool:
    with open('ids.txt', 'r') as ids:
        lines = ids.readlines()
        return post_id + subreddit +'\n' in lines


def insert(post_id: str, subreddit: str):
    with open('ids.txt', 'a') as ids:
        ids.write(post_id + subreddit + '\n')
