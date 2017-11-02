# Creating a one-file windows executable

Distributing python packages for use on Windows machines is
a bit problematic specially if using multiprocessing since
windows uses the "spawn" method to start a process.

Official documentation about "spawn":

The parent process starts a fresh python interpreter process. The child
process will only inherit those resources necessary to run the process objects
`run()` method. In particular, unnecessary file descriptors and handles from the
parent process will not be inherited. Starting a process using this method is
rather slow compared to using `fork` or `forkserver`.


For more details and caveats please see:

- https://docs.python.org/3.6/library/multiprocessing.html#miscellaneous
- https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
- http://rhodesmill.org/brandon/2010/python-multiprocessing-linux-windows/
- http://docs.python-guide.org/en/latest/shipping/freezing/


# Environment setup

OS: Win10 32bit

Microsoft Visual C++ 2010 Redistributable Package (x86): https://www.microsoft.com/en-us/download/details.aspx?id=5555

Python packages:

    pip install virtualenvwrapper==4.8.2
    pip install pypiwin32==219 
    pip install PyInstaller==3.2


# Packaging

Get a fresh copy of the repository and update the **DEFAULT_VERISON**
variable in [onefl/version.py](onefl/version.py) file.
This step is necessary since both "recommended" methods for detecting 
the package version fail ("pkg_resources" and "setuptools_scm.get_version()")

Run the command to create the exe file:

    $ pyinstaller --onefile --icon resources/lock_icon.ico run/hasher.py 


Generate a signature for the file to allow checking the file integrity:

    $ sha1sum.exe dist/hasher.exe
    cf4dbf641b72dbcd6d9640901589d275191ee88d *dist/hasher.exe
