import logging
import re
import time
from typing import Callable, Any, List

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
            if error_count > 3:
                util_logger.error('Retried to call <{}> 3 times without success. '
                                  'Continuing without calling it.'.format(func.__name__))
                break

            if 'DELETED_COMMENT' in str(e):
                util_logger.warning('The comment has been deleted. '
                                    'Function <{}> was not executed.'.format(func.__name__))
                break
            wait = parse_wait_time(str(e))
            util_logger.error(e)
            util_logger.warning('Waiting ~{} minutes'.format(round(float(wait + 30) / 60)))
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


def init_reddit(creds_path='creds.props') -> praw.Reddit:
    """Initialize the reddit session by reading the credentials from the file at :code:`creds_path`.

    :param creds_path: Properties file with the credentials.

    **Example file**::

        client_id=CLIENT_ID
        client_secret=CLIENT_SECRET
        password=PASSWORD
        user_agent=USER_AGENT
        username=USERNAME
    """
    with open(creds_path) as f:
        prop_lines = [l.replace('\n','').split('=') for l in f.readlines()]
        f.close()
        props = {l[0]: l[1] for l in prop_lines}
        return praw.Reddit(**props)


def get_subs(subs_file='subreddits.txt', blacklist_file='blacklist.txt') -> List[str]:
    """
    Get subs based on a file of subreddits and a file of blacklisted subreddits.

    :param subs_file: List of subreddits. Each sub in a new line.
    :param blacklist_file:  List of blacklisted subreddits. Each sub in a new line.
    :return: List of subreddits filtered with the blacklisted subs.

    **Example files**::

        sub0
        sub1
        sub2
        ...
    """
    # Get subs and blacklisted subs
    subsf = open(subs_file)
    blacklf = open(blacklist_file)
    subs = [b.lower().replace('\n','') for b in subsf.readlines()]
    blacklisted = [b.lower().replace('\n','') for b in blacklf.readlines()]
    subsf.close()
    blacklf.close()

    # Filter blacklisted
    subs_filtered = list(sorted(set(subs).difference(set(blacklisted))))
    return subs_filtered