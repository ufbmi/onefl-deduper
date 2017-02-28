# Installation Steps - Windows

# Create a virtualenv

- download and install the latest python 3 release (python >= 3.4) from 
[Python Releases for Windows](https://www.python.org/downloads/windows/) page

Note: Make sure that you have the option **"Add Python to environment variables"**
checked when asked during installation.

Example of python installation url:
    [python-3.5.2-amd64.exe](https://www.python.org/ftp/python/3.5.2/python-3.5.2-amd64.exe)

- install [git-for-windows](https://git-for-windows.github.io/)

- start the "Git Bash" executable and verify that the latest version of the
**pip** utility is installed

        $ pip --version
        $ python -m pip install --upgrade pip

- create a folder for storing dependencies

        $ cd ~
        $ mkdir .virtualenvs

- install the helper tool for isolating the installation files

        $ pip install virtualenv

- activate the isolation environment

        $ virtualenv deduper
        $ source deduper/Scripts/activate

- verify that the prompt has changed and indicates **(deduper)**
as an active python environment


# Install and configure

The steps for this section are similar to the
[docs/installation-redhat.md](installation-redhat.md#Install and configure)
so please follow them.


# Installation Steps - Windows without internet connection


1. Download the packages on a machine which *does* have internet connection:

    $ mkdir my_pypi && cd my_pypi
    $ pip download --platform=windows --only-binary=:all: virtualenv virtualenvwrapper invoke deduper

2. Transfer the `my_pypi` folder to the restricted windows environment

3. Install the packages from within the `my_pypi` folder

    $ cd C:\Users\asura\my_pypi
    $ pip install --no-index --find-links=. --root=. pbr six stevedore invoke virtualenv
    $ pip install --no-index --find-links=. --root=. deduper
