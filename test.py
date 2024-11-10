from . import memelang as ml

def test_basic_exprs():
    exprs = [('A', 'SELECT * FROM meme.meme WHERE aid=$1', ['A']),
             ('A.R', 'SELECT * FROM meme.meme WHERE aid=$1 AND rid=$2', ['A','R']),
             ("A'R", 'SELECT * FROM meme.meme WHERE rid=$1 AND bid=$2', ['R', 'A']),
             ('A.R:B', 'SELECT * FROM meme.meme WHERE aid=$1 AND rid=$2 AND bid=$3', ['A','R','B']),
             ('A:B', 'SELECT * FROM meme.meme WHERE aid=$1 AND bid=$2', ['A','B']),
             ('.R', 'SELECT * FROM meme.meme WHERE rid=$1', ['R']),
             ('.R:B', 'SELECT * FROM meme.meme WHERE rid=$1 AND bid=$2', ['R','B']),
             (':B', 'SELECT * FROM meme.meme WHERE bid=$1', ['B']),
             ('A.Rx | A.Ry', 'SELECT * FROM meme.meme WHERE aid=$1 AND rid=$2 UNION SELECT * FROM meme.meme WHERE aid=$3 AND rid=$4', ['A', 'Rx', 'A', 'Ry']),
             ('A.Rx & A.Ry', 'SELECT * FROM meme.meme WHERE EXISTS (SELECT * FROM meme.meme WHERE aid=$1 AND rid=$2) AND EXISTS (SELECT * FROM meme.meme WHERE aid=$3 AND rid=$4)', ['A', 'Rx', 'A', 'Ry']),
             ('A.R:B += 10', 'SELECT aid,rid,bid,qnt + 10 AS qnt FROM meme.meme WHERE aid=$1 AND rid=$2 AND bid=$3', ['A', 'R', 'B'])
             ]
    for (memelang_expr, expected_sql, expected_params) in exprs:
        (sql, params) = ml.compile_sql(ml.parse(ml.tokenize(memelang_expr)))
        assert sql == expected_sql
        assert params == expected_params
        
