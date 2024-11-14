# memelang for postgres

Implements [memelang](https://memelang.net/) as a function within postgresql.

## Installation

Ensure that pl/plython is installed in your postgresql installation.

On Ubuntu 20.04: `sudo apt install postgresql-plpython3-12`

On Ubuntu 24.04: `sudo apt install postgresql-plpython3-16`

Run SQL installation script:

`psql -f memelang_plpythonu_setup.sql <target db>`

## Usage:

Populate the meme.meme table with some values:

```SQL
=# insert into meme.meme(aid,rid,bid,qnt) values ('A','R','B',1),('Alice','uncle','Bob',1);
```

Run your memelang query:

```SQL
SELECT * FROM meme.query('A.R:B');
```

## Build

`memelang.py` contains the core lexer, parser, and SQL compiler for memelang.

`mkplpython.py` reads `memelang.py`, runs `stickytape` to pull funcparserlib into a single script `memelang_bundle.py` which is then wrapped into an SQL installer script at `memelang_plpythonu_setup.sql`

## Testing

`pytest test.py`