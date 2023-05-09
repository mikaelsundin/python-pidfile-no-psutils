Python PIDFile
==============

Python context manager for managing pid files. Example usage:

.. code-block:: python

    import pidfile
    import time

    print('Starting process')
    try:
        with pidfile.PIDFile("/var/run/example.pid"):
            print('Process started')
            time.sleep(30)
    except pidfile.AlreadyRunningError:
        print('Already running.')

    print('Exiting')

The context manager will take care of verifying the existence of a pid file,
check its pid to see if it's alive, check the command line (which should be `<something>/<python name>`), and
if all the conditions are met, rise a `pidfile.AlreadyRunningError` exception.

`PIDFile()` defaults to `pidfile` for the file name, but it's possible to specify another, e.g. `PIDFile('foobar.pid')`.


Under the hood
--------------

The algorithm of the library is very simple, at startup, a file is created,
and after checking that another instance of the program is not running, the
current process ID is written to it.

The check works as follows:

* If the file does not exist, then the check is passed.
* An identifier is written in the file, it is read and checked that a
  process running with such an identifier exists, and has the same command line.
