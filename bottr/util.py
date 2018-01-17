import logging
import re

import time

import praw

"""Rate limit regular expression to extrect the time in minutes/seconds"""
RATELIMIT = re.compile(r'in (\d+) (minutes|seconds)')


def parse_wait_time(text: str) -> int:
    """Parse the waiting time from the exception"""
    val = RATELIMIT.findall(text)
    if len(val) > 0:
        try:
            res = val[0]
            if res[1] == 'minutes':
                return int(res[0]) * 60

            if res[1] == 'seconds':
                return int(res[0])
        except Exception as e:
            logging.warn('Could not parse ratelimit: ' + str(e))
    return 1 * 60


def handle_ratelimit(func: staticmethod, *args, **kwargs):
    """Execute func and handle rate limit exceptions"""
    error_count = 0
    while True:
        try:
            func(*args, **kwargs)
            time.sleep(15)
            break
        except Exception as e:
            if error_count > 10:
                logging.error('Retried to call <{}> 10 times without success. Continuing without calling it.'.format(
                    func.__name__))
                break
            logging.error(e)
            wait = parse_wait_time(str(e))
            logging.warning('Waiting ~{} minutes'.format(round(float(wait + 30) /
                                                               60)))
            time.sleep(wait + 30)
            error_count += 1

def check_depth(comment: praw.models.Comment, max_depth=3) -> int:
    """
    Check if comment is in allowed depth range
    :param comment: Comment to count the depth
    :param max_depth: Max. allowed depth
    :return: True if comment is in depth range between 0 and max_depth
    """
    count = 0
    while not comment.is_root:
        comment = comment.parent()
        count += 1
        if count > max_depth:
            return False

    return True