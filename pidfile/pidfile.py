import atexit
import os
import subprocess
from typing import Any

class AlreadyRunningError(Exception):
    pass


class PIDFile(object):
    def __init__(self, filename: Any = "pidfile"):
        self._process_name = self.process_cmdline(os.getpid())
        self._file = str(filename)

    def process_cmdline(self, pid: int) -> str:
        """Use subprocess instead of psutil, return empty string if the process is not found"""
        output = subprocess.check_output(["ps", "-p", str(pid), "-o", "args="])
        return output.decode().split()[0]
    
    def pid_exists(self, pid: int) -> bool:
        """Check if pid exist on posix systems"""
        if pid == 0:
            return True
            
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            #No process found
            return False
        except PermissionError:
            # EPERM clearly means there's a process to deny access to
            return True
        else:
            # (EINVAL, EPERM, ESRCH)
            return True

    @property
    def is_running(self) -> bool:
        if not os.path.exists(self._file):
            return False

        with open(self._file, "r") as f:
            try:
                pid = int(f.read())
            except (OSError, ValueError):
                return False

        #check if the PID exist as a running process
        if not self.pid_exists(pid):
            return False

        #check if the arguments is the same as our executable
        return self.process_cmdline(pid) == self._process_name


    def close(self) -> None:
        if os.path.exists(self._file):
            try:
                os.unlink(self._file)
            except OSError:
                pass

    def __enter__(self) -> "PIDFile":
        if self.is_running:
            raise AlreadyRunningError

        with open(self._file, "w") as f:
            f.write(str(os.getpid()))

        atexit.register(self.close)

        return self

    def __exit__(self, *_) -> None:
        self.close()
        atexit.unregister(self.close)
