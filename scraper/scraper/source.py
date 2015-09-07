# Copyright 2015 Adam Greenstein <adamgreenstein@comcast.net>
#
# Switcharoo Cartographer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Switcharoo Cartographer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Switcharoo Cartographer.  If not, see <http://www.gnu.org/licenses/>.

import time

from data import Access
from Queue import Empty


class Source:
    def __init__(self, transverse):
        self.t = transverse

    def get_new_submissions(self, limit=10):
        bad_flairs = ('meta', 'Reported faulty')
        size = self.t.queue.qsize()
        submissions = self.t.reddit.get_subreddit('switcharoo').get_hot(limit=limit)
        for submission in submissions:
            if submission.link_flair_text not in bad_flairs:
                self.t.queue.put(submission.url)
            else:
                self.t.events.on_skipping_url(submission.url)
        return self.t.queue.qsize() > size

    def add_to_queue(self, limit, sleep=10):
        try:
            current_entry = self.t.queue.get_nowait()
        except Empty:
            while not self.get_new_submissions(limit):
                self.t.events.waiting(sleep)
                time.sleep(sleep)
            current_entry = self.t.queue.get_nowait()
        self.t.events.using_url(current_entry.raw_url)
        return current_entry

    def mark_searched(self, entry):
        Access(self.t.events).mark_searched(entry)