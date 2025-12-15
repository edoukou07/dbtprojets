"""
Custom logging handlers for Windows compatibility
Fixes the PermissionError when rotating log files on Windows
"""
import os
import shutil
import logging
from logging.handlers import RotatingFileHandler


class WindowsCompatibleRotatingFileHandler(RotatingFileHandler):
    """
    RotatingFileHandler compatible with Windows.
    
    On Windows, renaming a file that's open fails with PermissionError.
    This handler closes the file before renaming, then reopens it.
    """
    
    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        Override to handle Windows file locking issues by closing the file before rotation.
        """
        # Close the stream before rotation to avoid Windows file locking issues
        if self.stream:
            self.stream.close()
            self.stream = None
        
        if self.backupCount > 0:
            # Delete the oldest backup if it exists
            s = self.baseFilename + '.' + str(self.backupCount)
            if os.path.exists(s):
                try:
                    os.remove(s)
                except OSError:
                    pass
            
            # Rotate all backups (from oldest to newest)
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.baseFilename + "." + str(i)
                dfn = self.baseFilename + "." + str(i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        try:
                            os.remove(dfn)
                        except OSError:
                            pass
                    try:
                        # Use shutil.move instead of os.rename for better Windows compatibility
                        shutil.move(sfn, dfn)
                    except OSError:
                        pass
            
            # Rotate the main log file
            dfn = self.baseFilename + ".1"
            if os.path.exists(self.baseFilename):
                if os.path.exists(dfn):
                    try:
                        os.remove(dfn)
                    except OSError:
                        pass
                try:
                    # Use shutil.move instead of os.rename for Windows compatibility
                    shutil.move(self.baseFilename, dfn)
                except OSError:
                    pass
        
        # Reopen the stream
        if not self.delay:
            self.stream = self._open()

