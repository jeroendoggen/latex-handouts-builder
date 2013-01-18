""" Build Script for Latex-beamer based course handouts

Copyright (C) 2013  Jeroen Doggen <jeroendoggen@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys
import build_multi
#import build_single

def run():
    """Run the main program"""
    return(build_multi.run())
    #return(build_single.run())


if __name__ == "__main__":
    sys.exit(run())
 
