####################################################################################################
#    Copyright (C) 2016 by Ingo Keller                                                             #
#    <brutusthetschiepel@gmail.com>                                                                #
#                                                                                                  #
#    This file is part of yarpTab (OS X Menu Tab for YARP).                                        #
#                                                                                                  #
#    yarpTab is free software: you can redistribute it and/or modify it under the terms of the     #
#    GNU Affero General Public License as published by the Free Software Foundation, either        #
#    version 3 of the License, or (at your option) any later version.                              #
#                                                                                                  #
#    yarpTab is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;          #
#    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.     #
#    See the GNU General Public License for more details.                                          #
#                                                                                                  #
#    You should have received a copy of the GNU Affero General Public License                      #
#    along with yarpTab.  If not, see <http://www.gnu.org/licenses/>.                              #
####################################################################################################
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

APP         = ['yarpTab.py']
DATA_FILES  = []
PKGS        = ['rumps', 'Foundation', 'objc']
OPTIONS     = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': PKGS,
}

setup(
    app             = APP,
    data_files      = DATA_FILES,
    name            = "yarpTab",
    options         = {'py2app': OPTIONS},
    setup_requires  = ['py2app'],
    version         = 0.1,
)
