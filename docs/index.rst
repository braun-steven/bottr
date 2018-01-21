.. bottr documentation master file, created by
   sphinx-quickstart on Thu Jan 18 16:16:06 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to bottr's documentation!
=================================

Bottr is supposed to make writing bots for reddit easy. It relies on the `Python Reddit API Wrapper`
`PRAW <http://praw.readthedocs.io/en/latest/index.html>`_.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   setup
   bots
   util

Check out `bottr-template <https://github.com/slang03/bottr-template>`_ for a convenient code template to start with.

Quick Start
-----------

The following is a quick example on how to monitor `r/AskReddit` for new comments. If a comment
contains the string :code:`'banana'`, the bot replies :code:`'This comment is bananas.'`::

   import praw
   import time

   from bottr.bot import CommentBot

   def parse_comment(comment):
       """Define what to do with a comment"""
       if 'banana' in comment.body:
           comment.reply('This comment is bananas.')

   if __name__ == '__main__':

       # Get reddit instance with login details
       reddit = praw.Reddit(client_id='id',
                            client_secret='secret',
                            password='botpassword',
                            user_agent='Script by /u/...',
                            username='botname')

       # Create Bot with methods to parse comments
       bot = CommentBot(reddit=reddit,
                       func_comment=parse_comment,
                       subreddits=['AskReddit'])

       # Start Bot
       bot.start()

       # Run bot for 10 minutes
       time.sleep(10*60)

       # Stop Bot
       bot.stop()

Check out :ref:`setup` to see how to get the arguments for :class:`praw.Reddit`.

.. note::
   Please read the reddit `bottiquette <https://www.reddit.com/wiki/bottiquette>`_ if you intend to
   run a bot that interacts with reddit, such as writing submissions/comments etc.