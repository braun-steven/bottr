.. _bots:

Predefined Bots
===============


* :ref:`comment_bot`
* :ref:`submission_bot`

Description
-----------

Bottr comes with two predefined bots, :class:`CommentBot` and :class:`SubmissionBot`.
Both bots accepts a function as constructor argument. The bots listen to a stream of new
comments/submissions and call the given function with a :class:`praw.models.Comment` or
:class:`praw.models.Submission` object respectively.

The parsing function for comments or submissions might take some time, e.g. calling
:func:`praw.models.Comment.parent` makes a new request to the reddit api and waits for a response.
Therefore, it is possible to specify the argument :code:`n_jobs` when creating the bots.
This is the maximum number of comments/submissions that can be processed in parallel by the bot.
The stream of new comments/submissions are internally put into a :class:`~queue.Queue`, being
available to a list of worker threads that successively poll new objects to process from the queue.
The :code:`n_jobs` argument defines how many worker threads are available.

Bot Objects
-----------

.. _comment_bot:

Comment Bot
***********

.. autoclass:: bottr.bot.CommentBot
    :members:
    :inherited-members:
    :special-members: __init__


.. _submission_bot:

Submission Bot
**************

.. autoclass:: bottr.bot.SubmissionBot
    :members:
    :inherited-members:
    :special-members: __init__

