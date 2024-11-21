# memelang for postgres

Implements [memelang](https://memelang.net/) as a function within postgresql.

## Installation

### For Ubuntu 24.04:

`bash memelang_install.sh`

### For other platforms:

Ensure that pl/plython is installed in your postgresql installation.

On Ubuntu 20.04: `sudo apt install postgresql-plpython3-12`

On Ubuntu 24.04: `sudo apt install postgresql-plpython3-16`

Run SQL installation script:

`psql -f memelang_plpythonu_setup.sql <target db>`

## Usage:

Populate the meme.meme table with some values:

```SQL
=# insert into meme(aid,rid,bid,qnt) values ('A','R','B',1),('Alice','uncle','Bob',1);
```

Run your memelang query:

```SQL
SELECT * FROM meme.query('A.R:B');
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