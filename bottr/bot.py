import argparse
import logging
import threading
import time
from abc import ABC, abstractmethod
from queue import Queue
from typing import Iterable

import praw

class AbstractBot(ABC):
    """
    Abstract bot class.
    """

    def __init__(self, name: str, reddit: praw.Reddit, subs: Iterable = None, n_jobs=4,
                 thread_sleep_time=10):
        """
        Default constructor

        :param name: Bot name
        :param reddit: Reddit instance
        :param subs: List of subreddits
        :param n_jobs: Number of jobs for parallelization
        :param thread_sleep_time: Sleep time to wait until more threads are available
        """

        if subs is None:
            subs = []

        self._subs = subs
        self._name = name
        self._reddit = reddit
        self._n_jobs = n_jobs
        self._thread_sleep_time = thread_sleep_time
        self._processes_comments = False
        self._processes_submissions = False
        super().__init__()

    @abstractmethod
    def process_comment(self, comment: praw.models.Comment):
        """Process a single comment"""
        pass

    @abstractmethod
    def process_submission(self, submission: praw.models.Submission):
        """Process a single submission"""
        pass

    def listen_comments(self):
        # Collect submissions in a queue
        comments_queue = Queue()

        # Create n_jobs CommentsThreads
        for i in range(self._n_jobs):
            t = CommentBotThread('CommentThread-t-{}'.format(i), comments_queue, self)
            t.start()

        # Iterate over all comments in the comment stream
        for comment in self._reddit.subreddit('+'.join(self._subs)).stream.comments():
            comments_queue.put(comment)

    def listen_submissions(self):
        # Collect submissions in a queue
        subs_queue = Queue()

        # Create n_jobs SubmissionThreads
        for i in range(self._n_jobs):
            t = SubmissionBotThread('SubmissionThread-t-{}'.format(i), subs_queue, self)
            t.start()

        # Iterate over all comments in the comment stream
        for submission in self._reddit.subreddit('+'.join(self._subs)).stream.submissions():
            subs_queue.put(submission)

    def start(self):
        """Start this bot."""
        logging.info('Starting {} bot'.format(self._name))

        # Run comments stream if enabled
        if self._processes_comments:
            comments_thread = CommentStreamBotThread('{}-comments-stream-thread'.format(self._name),
                                                     bot=self)
            comments_thread.start()

        # Run submissions stream if enabled
        if self._processes_submissions:
            submissions_thread = SubmissionStreamBotThread(
                '{}-submissions-stream-thread'.format(self._name), bot=self)
            submissions_thread.start()

class BotThread(threading.Thread, ABC):
    """
    A thread running bot tasks.
    """

    def __init__(self, name: str, bot: AbstractBot = None, *args):
        threading.Thread.__init__(self)
        self._args = args
        self._bot = bot
        self.name = name

    def run(self):
        self._call()

    @abstractmethod
    def _call(self, *args):
        pass


class BotQueueWorker(BotThread):

    def __init__(self, name: str, jobs: Queue = None, bot: AbstractBot = None, *args):
        super().__init__(name=name, bot=bot, *args)
        self._jobs = jobs

    @abstractmethod
    def _process(self, job):
        pass

    def _call(self, *args):
        while True:
            e = self._jobs.get()
            logging.debug('{} processing element: {}'.format(self._name, e))
            # If nothing to do: sleep
            if e is None:
                time.sleep(10)
                continue
            self._process(e)
            self._jobs.task_done()


class CommentBotThread(BotQueueWorker):
    def _process(self, job):
        self._bot.process_comment(job)


class SubmissionBotThread(BotQueueWorker):
    def _process(self, job):
        self._bot.process_submission(job)


class SubmissionStreamBotThread(BotThread):
    def _call(self):
        self._bot.listen_submissions()


class CommentStreamBotThread(BotThread):
    def _call(self, *args):
        self._bot.listen_comments()
