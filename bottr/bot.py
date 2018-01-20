import logging
import threading
import time
from abc import ABC, abstractmethod
from queue import Queue
from typing import Iterable, List, Callable

import praw


class AbstractBot(ABC):
    """
    Abstract bot class.
    """

    def __init__(self, reddit: praw.Reddit,
                 subreddits: Iterable = None,
                 name: str = "AbstractBot",
                 n_jobs=4, ):
        """
        Default constructor

        :param reddit: Reddit instance
        :param subreddits: List of subreddits
        :param n_jobs: Number of jobs for parallelization
        """

        if subreddits is None:
            subreddits = []  # type: List[str]

        if n_jobs < 1:
            raise Exception('You need at least one worker thread.')

        self._subs = subreddits
        self._name = name
        self._reddit = reddit
        self._n_jobs = n_jobs
        self._stop = False
        self._threads = []  # type: List[BotThread]
        self.log = logging.getLogger(__name__)
        super().__init__()

    @abstractmethod
    def start(self):
        """
        Start this bot.
        """
        pass

    def stop(self):
        """
        Stops this bot.

        Returns as soon as all running threads have finished processing.
        """
        self.log.debug('Stopping bot {}'.format(self._name))
        self._stop = True
        for t in self._threads:
            t.join()

        self.log.debug('Stopping bot {} finished. All threads joined.'.format(self._name))

    def _do_stop(self, q: Queue, threads: List[threading.Thread]):
        # For each thread: put None into the queue to stop the thread from polling
        for i in range(self._n_jobs):
            q.put(None)

        # Join threads
        for t in threads:
            t.join()


class AbstractCommentBot(AbstractBot):
    @abstractmethod
    def _process_comment(self, comment: praw.models.Comment):
        """Process a single comment"""
        pass

    def _listen_comments(self):
        """Start listening to comments, using a separate thread."""
        # Collect comments in a queue
        comments_queue = Queue(maxsize=self._n_jobs * 4)

        threads = []  # type: List[BotQueueWorker]

        try:

            # Create n_jobs CommentsThreads
            for i in range(self._n_jobs):
                t = BotQueueWorker(name='CommentThread-t-{}'.format(i),
                                   jobs=comments_queue,
                                   target=self._process_comment)
                t.start()
                threads.append(t)

            # Iterate over all comments in the comment stream
            for comment in self._reddit.subreddit('+'.join(self._subs)).stream.comments():

                # Check for stopping
                if self._stop:
                    self._do_stop(comments_queue, threads)
                    break

                comments_queue.put(comment)

            self.log.debug('Listen comments stopped')
        except Exception as e:
            self._do_stop(comments_queue, threads)
            self.log.error('Exception while listening to comments:')
            self.log.error(str(e))
            self.log.error('Waiting for 10 minutes and trying again.')
            time.sleep(10 * 60)

            # Retry
            self._listen_comments()

    def start(self):
        """
        Starts this bot in a separate thread. Therefore, this call is non-blocking.

        It will listen to all new comments created in the :attr:`~subreddits` list.
        """
        super().start()
        comments_thread = BotThread(name='{}-comments-stream-thread'.format(self._name),
                                    target=self._listen_comments)
        comments_thread.start()
        self._threads.append(comments_thread)
        self.log.info('Starting comments stream ...')


class AbstractSubmissionBot(AbstractBot):
    @abstractmethod
    def _process_submission(self, submission: praw.models.Submission):
        """Process a single submission"""
        pass

    def _listen_submissions(self):
        """Start listening to submissions, using a separate thread."""
        # Collect submissions in a queue
        subs_queue = Queue(maxsize=self._n_jobs * 4)

        threads = []  # type: List[BotQueueWorker]

        try:
            # Create n_jobs SubmissionThreads
            for i in range(self._n_jobs):
                t = BotQueueWorker(name='SubmissionThread-t-{}'.format(i),
                                   jobs=subs_queue,
                                   target=self._process_submission)
                t.start()
                self._threads.append(t)

            # Iterate over all comments in the comment stream
            for submission in self._reddit.subreddit('+'.join(self._subs)).stream.submissions():

                # Check for stopping
                if self._stop:
                    self._do_stop(subs_queue, threads)
                    break

                subs_queue.put(submission)

            self.log.debug('Listen submissions stopped')
        except Exception as e:
            self._do_stop(subs_queue, threads)
            self.log.error('Exception while listening to submissions:')
            self.log.error(str(e))
            self.log.error('Waiting for 10 minutes and trying again.')
            time.sleep(10 * 60)

            # Retry:
            self._listen_submissions()

    def start(self):
        """
        Starts this bot in a separate thread. Therefore, this call is non-blocking.

        It will listen to all new submissions created in the :attr:`~subreddits` list.
        """
        super().start()
        submissions_thread = BotThread(name='{}-submissions-stream-thread'.format(self._name),
                                       target=self._listen_submissions)
        submissions_thread.start()
        self._threads.append(submissions_thread)
        self.log.info('Starting submissions stream ...')


class CommentBot(AbstractCommentBot):
    """
    This bot listens to incoming comments and calls the provided method :code:`func_comment` as
    :code:`func_comment(comment, *func_comment_args)` for each :code:`comment` that is submitted in
    the given :code:`subreddits`.

    Creates a bot that listens to comments in a list of subreddits and calls a given
    function on each new comment.

    :param reddit: :class:`praw.Reddit` instance. Check :ref:`setup` on how to create it.
    :param name: Bot name
    :param func_comment: Comment function. It needs to accept a :class:`praw.models.Comment`
        object and may take more arguments. For each comment created in :code:`subreddits`, a
        :class:`praw.models.Comment` object and all :code:`fun_comments_args` are passed to
        :code:`func_comment` as arguments.
    :param func_comment_args: Comment function arguments.
    :param subreddits: List of subreddit names. Example: :code:`['AskReddit', 'Videos', ...]`
    :param n_jobs: Number of parallel threads that are started when calling
        :func:`~CommentBot.start` to process in the incoming comments.

    **Example usage**::

        # Write a parsing method
        def parse(comment):
           if 'banana' in comment.body:
               comment.reply('This comment is bananas.')

        reddit = praw.Reddit(...) # Create a PRAW Reddit instance
        bot = CommentBot(reddit=reddit, func_comment=parse)
        bot.start()

    """

    def __init__(self, reddit: praw.Reddit,
                 name: str = "CommentBot",
                 func_comment: Callable[[praw.models.Comment], None] = None,
                 func_comment_args: List = None,
                 subreddits: Iterable = None,
                 n_jobs=4):
        super().__init__(reddit, subreddits, name, n_jobs)

        # Enable comment processing if proper method was given
        if func_comment is not None:
            if func_comment_args is None:
                func_comment_args = []

            self._func_comment = func_comment
            self._func_comment_args = func_comment_args

    def _process_comment(self, comment: praw.models.Comment):
        """
        Process a reddit comment. Calls `func_comment(*func_comment_args)`.

        :param comment: Comment to process
        """
        self._func_comment(comment, *self._func_comment_args)


class SubmissionBot(AbstractSubmissionBot):
    """
    Bottr Bot instance that can take a method :code:`func_submission` and calls that method as
    :code:`func_submission(submission, *func_submission_args)`

    Can listen to new submissions made on a given list of subreddits.

    :param reddit: :class:`praw.Reddit` instance. Check `here
        <http://praw.readthedocs.io/en/latest/code_overview/reddit_instance.html#praw.Reddit>`_
        on how to create it.
    :param name: Bot name
    :param func_submission: Submission function. It needs to accept a :class:`praw.models.Submission`
        object and may take more arguments. For each submission created in :code:`subreddits`, a
        :class:`praw.models.Submission` object and all :code:`fun_submission_args` are passed to
        :code:`func_submission` as arguments.
    :param func_submission_args: submission function arguments.
    :param subreddits: List of subreddit names. Example: :code:`['AskReddit', 'Videos', ...]`
    :param n_jobs: Number of parallel threads that are started when calling
        :func:`~SubmissionBot.start` to process in the incoming submissions.


    **Example usage**::

        # Write a parsing method
        def parse(submission):
            if 'banana' in submission.title:
                submission.reply('This submission is bananas.')

        reddit = praw.Reddit(...) # Create a PRAW Reddit instance
        bot = SubmissionBot(reddit=reddit, func_submission=parse)
        bot.start()

    """

    def __init__(self, reddit: praw.Reddit,
                 name: str = "SubmissionBot",
                 func_submission: Callable[[praw.models.Comment], None] = None,
                 func_submission_args: List = None,
                 subreddits: Iterable = None,
                 n_jobs=4):
        super().__init__(reddit, subreddits, name, n_jobs)

        # Enable comment processing if proper method was given
        if func_submission is not None:
            if func_submission_args is None:
                func_submission_args = []

            self._func_submission = func_submission
            self._func_submission_args = func_submission_args

    def _process_submission(self, submission: praw.models.Submission):
        """
        Process a reddit submission. Calls `func_comment(*func_comment_args)`.

        :param submission: Comment to process
        """
        self._func_submission(submission, *self._func_submission_args)


class BotThread(threading.Thread, ABC):
    """
    A thread running bot tasks.
    """

    def __init__(self, name: str, target: classmethod = None, *args):
        threading.Thread.__init__(self)
        self._args = args
        self._target = target
        self.name = name
        self.log = logging.getLogger(__name__)

    def run(self):
        self._call()

    def _call(self):
        self._target(*self._args)


class BotQueueWorker(BotThread):
    """
    A worker thread that works on a given queue. It is polling new jobs from the queue and processes
    it.
    """

    def __init__(self, name: str, jobs: Queue = None, target: classmethod = None, *args):
        """
        Initialize this worker.
        :param name: Name
        :param jobs: Job queue
        :param bot: Bot object
        :param args: Additional arguments
        """
        super().__init__(name=name, target=target, *args)
        self._jobs = jobs

    def _call(self, *args):
        while True:

            # Blocks if no item available
            e = self._jobs.get()
            self.log.debug('{} processing element: {}'.format(self._name, e))

            # If None is in queue, exit
            if e is None:
                break

            # Process the element
            self._target(e, *args)
            self._jobs.task_done()
