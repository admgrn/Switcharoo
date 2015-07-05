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

from threading import Thread

class ConsoleManager:
    def __init__(self, transverse):
        self._methods = {}
        self._help = lambda x: ()
        self.transverse = transverse
        self.op = None

    def register(self, name, description='No description'):
        def func(fn):
            self._methods[name] = (fn, description)
            return fn
        return func

    def help(self, fn):
        self._help = fn
        return fn

    def console_loop(self):
        try:
            while 1:
                prompt_input = raw_input('Enter command or help >>> ')
                if prompt_input == 'help':
                    self._help([(k, self._methods[k][1]) for k in self._methods])
                elif prompt_input == 'exit':
                    break
                else:
                    inputs = prompt_input.split()
                    if len(inputs) == 0:
                        continue
                    elif len(inputs) > 1:
                        self._call(inputs[0], inputs[1:])
                    else:
                        self._call(inputs[0])
                        self.op = Thread(target=self._call, args=(inputs[0],))
        except KeyboardInterrupt:
            pass

    def _call(self, name, args=[]):
        try:
            if len(args) > 0:
                self._methods[name][0](*args)
            else:
                self._methods[name][0]()
        except TypeError:
            print ' > The command \'' + name + '\' does not take ' + str(len(args)) + ' arguments.'
        except KeyError:
            print ' > The command \'' + name + '\' does not exist.'
        except KeyboardInterrupt:
            pass