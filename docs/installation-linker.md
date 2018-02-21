# Steps for running the linker


## Checkout the github repository for onefl-deduper

    $ git checkout https://github.com/ufbmi/onefl-deduper.git
    $ cd onefl-deduper


## Create the database

Execute the following scripts on the SQLServer:

   [schema/000/upgrade.sql](schema/000/upgrade.sql)
   [schema/000/data.sql](schema/000/data.sql)


## Create the partners that you need to link, these partner names will be used later.

    INSERT INTO dbo.partner
        (partner_code, partner_description, partner_added_at)
    VALUES
        ('SOURCE_1', 'source 1', GETDATE()),
        ('SOURCE_2', 'source 2', GETDATE())


## Setup the python virtual environment

    $ mkvirtualenv deduper -p `which python3`
    $ pip install -r requirements-to-freeze.txt


## Obtain the source files

    $ cp some/long/path/file.csv data/partner_hashes.csv


## Create and update the config files as needed

    $ cp config/example/settings_linker.py.example config/settings_linker.py
    $ cp config/example/logs.cfg.example config/logs.cfg


Before running the linker for each source, update the following parameters
in the `config/settings_linker.py` file as needed.

    IN_DELIMITER - indicates what is the record separator (comma or tab)
    IN_FILE - the name of your input file (containing the PHI elements)
    OUT_FILE - the name of the file which will be sent to University of Florida
    DB_HOST - the name of the SQL server
    DB_NAME - the name of the SQL database
    DB_USER - the database service account name
    DB_PASS - the database service account pasword



## Run the linker by substituting the [PARTNER] by the actual partner name
in the following command
  
    $ PYTHONPATH=. python run/linker.py -i data -o data -p=PARTNERNAME --ask

When completed, you should be able to see new rows inserted in the database,
and an output file as  configured with `OUT_FILE` option.
