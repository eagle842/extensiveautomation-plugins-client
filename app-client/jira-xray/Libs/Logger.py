#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
# This file is part of the extensive automation project
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
# -------------------------------------------------------------------

"""
Python logger compatible with python 2.4
Based on logging python module, with log file rotation
"""

import logging
import logging.handlers
import time
import sys
import inspect

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    import Settings
except Exception as e:
    pass

def callee():
    """
    Callee
    """
    return inspect.getouterframes(inspect.currentframe())[1][1:4]

def caller():
    """
    Function to find out which function is the caller of the current function. 

    @return: caller function name
    @rtype: string
    """
    modulePath, lineNb, funcName =   inspect.getouterframes(inspect.currentframe())[2][1:4]
    return funcName

class ClassLogger(object):
    """
    Logger
    """
    def info (self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        try:
            instance().info(  unicode(txt).encode('utf-8')  )
        except:
            instance().info( txt  )
            
    def trace (self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        try:
            instance().debug(  unicode(txt).encode('utf-8')  )
        except:
            instance().debug(  txt )
            
    def error (self, err):
        """
        Log an error

        @param err:
        @type err:
        """
        try:
            instance().error( "%s > %s: %s" % ( self.__class__.__name__, caller(), unicode(err).encode('utf-8') ) )
        except:
            instance().error( "%s > %s: %s" % ( self.__class__.__name__, caller(), err ) )

LG = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return LG

def info (txt):
    """
    Log an info message

    @param txt:
    @type: txt: string
    """
    global LG
    LG.info( txt )

def error (txt):
    """
    Log an error message

    @param txt:
    @type: txt: string
    """
    global LG
    LG.error( txt )

def debug (txt):
    """
    Log a debug message

    @param txt:
    @type: txt: string
    """
    global LG
    LG.debug( txt )

def shutdown():
    """
    Shutdown
    """
    pass

def initialize (logPathFile=None, level="INFO", size="5", nbFiles="10", noSettings=False ):
    """
    Initialize

    @param logPathFile: complete path of the log file
    @type: logPathFile: string

    @param level: INFO | ERROR | DEBUG
    @type: level: string

    @param size: file size in megabytes
    @type: size: string

    @param nbFiles: number of log files
    @type: nbFiles: string
    """
    global LG
    if not noSettings:
        if logPathFile is not None:
            file = logPathFile
        else:
            file = "%s/%s" % ( Settings.getDirExec(), Settings.get( section = 'Trace', key = 'file' ) )
        level = Settings.get( section = 'Trace', key = 'level' )
        size = Settings.get( section = 'Trace', key = 'max-size-file' )
        maxBytes = int(size.split('M')[0]) * 1024 * 1024
        nbFilesMax = Settings.getInt( section = 'Trace', key = 'nb-backup-max' )
    else:
        file = logPathFile
        level = level
        size = size
        maxBytes = int(size.split('M')[0]) * 1024 * 1024
        nbFilesMax = nbFiles
    LG = logging.getLogger('Logger')
    LG.shutdown = shutdown
    if level == 'DEBUG':
        # write everything messages 
        LG.setLevel(logging.DEBUG)
    elif level == 'ERROR':
        # write anything that is an error or worse.
        LG.setLevel(logging.ERROR)
    elif level == 'INFO':
        # write anything that is an info message or worse.
        LG.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
                                                    file, 
                                                    maxBytes=maxBytes,
                                                    backupCount=nbFilesMax
                                                )
    
    #format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s',
    # %(funcName)s ==> not supported with python 2.4
    formatter = logging.Formatter( "%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    LG.addHandler(handler)
    
def reloadLevel(level="INFO"):
    """
    Reload Level
    """
    global LG
    if level == 'DEBUG':
        # write everything messages 
        LG.setLevel(logging.DEBUG)
    elif level == 'ERROR':
        # write anything that is an error or worse.
        LG.setLevel(logging.ERROR)
    elif level == 'INFO':
        # write anything that is an info message or worse.
        LG.setLevel(logging.INFO)
        
def finalize ():
    """
    Destroy Singleton
    """
    global LG
    if LG:
        if hasattr(LG, "shutdown"):
            LG.shutdown()
        LG = None