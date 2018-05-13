=====
bottr
=====

Bottr makes writing bots for reddit easy. It currently provides three predefined bots:

:CommentBot: Listens to new comments in a list of subreddits
:SubmissionBot: Listens to new submission in a list of subreddits
:MessageBot: Listens to new messages of the inbox

Bottr makes use of the `Python Reddit API Wrapper`
`PRAW <http://praw.readthedocs.io/en/latest/index.html>`_.

Documentation: `bottr.readthedocs.io <https://bottr.readthedocs.io>`_

Check out `bottr-template <https://github.com/slang03/bottr-template>`_ for a convenient code template to start with.

Installation
------------
Bottr is available on PyPi and can be installed via

.. code:: bash

    $ pip install bottr

:Latest version: :code:`0.1.4`

Quick Start
-----------

The following is a quick example on how to monitor `r/AskReddit` for new comments. If a comment
contains the string :code:`'banana'`, the bot prints the comment information

.. code:: python

   import praw
   import time

   from bottr.bot import CommentBot

   def parse_comment(comment):
       """Define what to do with a comment"""
       if 'banana' in comment.body:
           print('ID: {}'.format(comment.id))
           print('Author: {}'.format(comment.author))
           print('Body: {}'.format(comment.body))

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