import logging
import re
import time
from typing import Callable, Any

import praw

"""Rate limit regular expression to extract the time in minutes/seconds"""
RATELIMIT = re.compile(r'in (\d+) (minutes|seconds)')

util_logger = logging.getLogger(__name__)

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
            util_logger.warning('Could not parse ratelimit: ' + str(e))
    return 1 * 60


def handle_rate_limit(func: Callable[[Any], Any], *args, **kwargs) -> Any:
    """
    Calls :code:`func` with given arguments and handle rate limit exceptions.

    :param func: Function to call
    :param args: Argument list for :code:`func`
    :param kwargs: Dict arguments for `func`
    :returns: :code:`func` result
    """
    error_count = 0
    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if error_count > 10:
                util_logger.error('Retried to call <{}> 10 times without success. '
                              'Continuing without calling it.'.format(func.__name__))
                break
            util_logger.error(e)
            wait = parse_wait_time(str(e))
            util_logger.warning('Waiting ~{} minutes'.format(round(float(wait + 30) /
                                                                   60)))
            time.sleep(wait + 30)
            error_count += 1


def check_comment_depth(comment: praw.models.Comment, max_depth=3) -> bool:
    """
    Check if comment is in a allowed depth range

    :param comment: :class:`praw.models.Comment` to count the depth of
    :param max_depth: Maximum allowed depth
    :return: True if comment is in depth range between 0 and max_depth
    """
    count = 0
    while not comment.is_root:
        count += 1
        if count > max_depth:
            return False

        comment = comment.parent()

    return True
