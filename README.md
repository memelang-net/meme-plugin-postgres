# [memelang](https://memelang.net) for postgres

Implements [memelang](https://memelang.net/) as a function within postgresql.

License: [Memelicense.net](https://Memelicense.net)

## Installation

### For Ubuntu 24.04:

```bash
#!/bin/bash
set -ex

# Update and install dependencies
sudo apt update
sudo apt install -y python3 python3-pip pythonpy python3-pytest postgresql postgresql-plpython3-16 git git-core

# Start PostgreSQL service
sudo systemctl start postgresql

# Clone the repository
git clone https://gitlab.com/CodeDarkin/memelang.git
cd memelang

# Set up PostgreSQL with embedded commands
sudo -u postgres psql -c "CREATE DATABASE meme;"
sudo -u postgres psql -d meme -c "CREATE EXTENSION plpython3u;"

# Run the setup SQL script
sudo -u postgres psql -d meme -f memelang_plpythonu_setup.sql

# Insert default data
sudo -u postgres psql -d meme -f data.sql
```

### For other platforms:

Ensure that pl/plython is installed in your postgresql installation.

On Ubuntu 20.04: `sudo apt install postgresql-plpython3-12`

Run SQL installation script:

`psql -f memelang_plpythonu_setup.sql meme`

## Usage:

Populate the meme.meme table with some values:

```SQL
=# INSERT INTO meme (aid, rid, bid, qnt) VALUES ('george_washington', 'education', 'grade_school', 1);
```

Run your memelang query:

```SQL
meme=# select * from meme.query('william_taft.occupation');
INFO:  SELECT * FROM meme WHERE aid=$1 AND rid=$2
     aid      |    rid     |                 bid                 |   qnt    
--------------+------------+-------------------------------------+----------
 william_taft | occupation | lawyer                              | 1.000000
 william_taft | occupation | solicitor_general                   | 1.000000
 william_taft | occupation | judge                               | 1.000000
 william_taft | occupation | governor_general_of_the_philippines | 1.000000
 william_taft | occupation | secretary_of_war                    | 1.000000
(5 rows)
```

## Build

Switch to "build" branch: `git checkout build`

`memelang.py` contains the core lexer, parser, and SQL compiler for memelang.

`mkplpython.py` reads `memelang.py`, runs `stickytape` to pull funcparserlib into a single script `memelang_bundle.py` which is then wrapped into an SQL installer script at `memelang_plpythonu_setup.sql`

## Testing

Switch to "build" branch: `git checkout build`

```
#install python venv
sudo apt install python3.12-venv
python3 -mvenv venv
#activate venv
source venv/bin/activate
#install dependencies
pip install -r requirements.txt
pip install pytest
#run the tests
python -m pytest test.py
```
