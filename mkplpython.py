import subprocess
import sys

bundle_path = 'memelang_bundle.py'

# run stickytape to pull funcparserlib into function body
subprocess.run(['stickytape', 'memelang.py',
                '--output-file', bundle_path,
                '--add-python-module', 'funcparserlib',
                '--python-binary', sys.executable], check=True)

# load up memelang bundle source
with open(bundle_path, 'r') as pyin:
    memelang_body = pyin.read()

# wrap up memelang source with SQL- note that this script deletes any previous versions of the meme table or functions
sql = f'''CREATE EXTENSION IF NOT EXISTS plpython3u;
DROP SCHEMA IF EXISTS meme CASCADE;
CREATE SCHEMA meme;
CREATE TABLE IF NOT EXISTS meme (aid varchar(255), rid varchar(255), bid varchar(255), qnt DECIMAL(20,6));
CREATE FUNCTION meme.query(memelang_in TEXT) RETURNS TABLE (LIKE meme) AS $$ {memelang_body}
return execute_memelang()
$$ LANGUAGE plpython3u;'''

# write sql to file
with open('memelang_plpythonu_setup.sql', 'w') as sqlout:
    sqlout.write(sql)
    
