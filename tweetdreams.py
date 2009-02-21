#!/usr/bin/env python
#
# Copyright 2009 Nicholas H.Tollervey (http://ntoll.org/)
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A library that generates new Tweets based upon the status histories of the
specified user's friends.

In a poetic sense, it creates dreams from the Jungian collective (un)conscience
that is the status history of your friends.

Depends on the Python/Twitter library found here:

    http://code.google.com/p/python-twitter/

Much of the code for the Markov chain was adapted from that found here:

    http://code.activestate.com/recipes/194364/
"""

__author__ = 'Nicholas H.Tollervey (http://ntoll.org/contact)'
__version__ = '0.1-alpha'

import random
import twitter

# By default, dreams cannot be longer than this number of characters
MAX_LENGTH = 140

class BadDream(Exception):
    """ Base class for dream errors"""

class Dream(object):
    """ An object to hold and process statuses into 'dreams'"""

    def __init__(self, username=None, password=None): 
        """Instantiate a new tweetdreams.Dream object.

        Args:
            username: The username of the twitter account. [required]
            password: The password for the twitter account. [required]
        """
        if username and password:
            self._api = twitter.Api(username, password)
            self._tweets = [] 
            self._table = {}
        else:
            raise BadDream('You must supply a username and/or password')

    def GetFriends(self):
        """ Proxy call to Twitter Api's GetFriends method"""
        return self._api.GetFriends()

    def GetTweets(self, friends = []):
        """ Given a list of friends will grab the most recent 200 tweets from
        each user and put them in a list"""
        for f in friends:
            # print 'Getting details for friend: %s'%f.screen_name
            try:
                tweet = self._api.GetUserTimeline(f.screen_name,200)
                self._tweets.extend(tweet)
            except HTTPError:
                # print HTTPError
                pass
        return self._tweets

    def Create(self, max_words = None):
        """ Returns a string created by a simple Markov chain based on the
        tweets from the user's friends"""

        # In case of first time run
        if not self._tweets:
            self.GetTweets(self.GetFriends())
        if not self._table:
            self._table = {}

        nonword = "\n" # Since we split on whitespace, this can never be a word
    
        for line in self._tweets:
            w1 = nonword
            w2 = nonword
            for word in line.text.split():
                self._table.setdefault( (w1, w2), [] ).append(word)
                w1, w2 = w2, word
            # Mark the end of the file
            self._table.setdefault( (w1, w2), [] ).append(nonword)         
        
        # Generate output
        w1 = nonword
        w2 = nonword
        result = [] 
        
        for i in xrange(max_words or 70): # 70 = more than enough
            newword = random.choice(self._table[(w1, w2)])
            #print table[(w1, w2)]
            #print newword
            if newword == nonword or newword.endswith('.'):
                break 
            result.append(newword)
            w1, w2 = w2, newword

        return (' '.join(result))[:MAX_LENGTH]
