=====
bottr
=====

Bottr is supposed to make writing bots for reddit easy. It relies on the `Python Reddit API Wrapper`
`PRAW <http://praw.readthedocs.io/en/latest/index.html>`_.


Quick Start
-----------

The following is a quick example on how to monitor `r/AskReddit` for new comments. If a comment
contains the string :code:`'banana'`, the bot replies :code:`'This comment is bananas'`

.. code:: python

   import praw

   def parse_comment(comment):
       """Define what to do with a comment"""
       if 'banana' in comment.body:
           comment.reply('This comment is bananas.')

   if __name__ == '__main__':

       # Get reddit instance with login details
       reddit = praw.Reddit(client_id='id',
                            client_secret='secret'',
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