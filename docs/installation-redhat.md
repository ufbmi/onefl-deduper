# Installation Steps - RedHat Linux

In the instructions below the name of the python package is `deduper` but
once the package is installed two commands are activated:

    $ hasher
    $ linker

For the sake of simplicity we assume that the reader is only interested
in the installation and configuration of the `hasher` component.
The linker component will be described in a separate document.

# Create a virtualenv

[virtualenv](https://virtualenv.pypa.io/en/stable/) is a tool to create isolated
Python environments.


- install python >= 3.4

        $ yum install python34-devel.x86_64

- install the python package manager (pip)

        $ yum install pip

- create a folder for storing dependencies

        $ mkdir ~/.virtualenvs

- install the helper tool for isolating the installation files

        $ pip install -U virtualenvwrapper

- activate the isolation environment

        $ export WORKON_HOME=$HOME/.virtualenvs
        $ source /usr/local/bin/virtualenvwrapper.sh
        $ mkvirtualenv deduper -p /usr/local/bin/python3

- verify that the prompt has changed and indicates **(deduper)**
as an active python environment


# Install and configure

We are using the standard python distribution model so installation 
should be relatively simple:

        $ pip --no-cache-dir install -U deduper

- create a directory for storing configuration and log files

        $ mkdir -p ~/deduper/logs

- create a config file by using the
[`config/example/settings_hasher.py.example`](https://github.com/ufbmi/onefl-deduper/blob/master/config/example/settings_hasher.py.example)
file as a template

        $ cp config/example/settings_hasher.py.example ~/deduper/settings_hasher.py

- edit the config file -- the `SALT` value

Note: we will provide the SALT to be used in production mode on request, for
the initial testing it is fine to leave it empty

        $ vim ~/deduper/settings_hasher.py

- generate an example input file called `phi.csv` with the following header:
`patid`, `first`, `last`, `dob`, `sex`, `race`

Notes:

- For testing purposes you can use the example file
[phi.csv](https://github.com/ufbmi/onefl-deduper/blob/master/tests/data_in/phi.csv).
- The example file uses `\t` as column separator.

        $ cp tests/data_in/phi.csv .

- display the package version and run it

        $ hasher -v
        $ hasher -c ~/deduper/settings_hasher.py

    You should get some output indicating that a file was produced:

        >> Wrote output file: ./phi_hashes.csv

    The output file should have the following columns: `patid`, `F_L_D_G`, `F_L_D_R`
