.. bottr documentation master file, created by
   sphinx-quickstart on Thu Jan 18 16:16:06 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to bottr's documentation!
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   intro


Quick Example
-------------

This is a quick example::

   def parse_comment(comment):
       """Define what to do with a comment"""
       if 'banana' in comment.body:
           comment.reply('This comment is bananas.')

   def parse_submission(submission):
       """Define what to do with a submission"""
       if 'banana' in submission.title:
           comment.reply('This submission is bananas.')


   if __name__ == '__main__':
       # Get reddit instance with login details
       reddit = praw.Reddit(client_id='id',
                            client_secret='secret'',
                            password='userpassword',
                            user_agent='Script by /u/...',
                            username='botname')

       # Create Bot with methods to parse comments/submission
       bot = RedditBot(reddit=reddit,
                       func_comment=parse_comment,
                       func_submission=parse_submission,
                       subs=["AskReddit"])

       # Start Bot
       bot.start()

       # Run bot for 10 seconds
       time.sleep(10*60)

       # Stop Bot
       bot.stop()

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
