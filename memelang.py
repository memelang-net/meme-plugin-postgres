from typing import List, Tuple, Union
from funcparserlib.lexer import make_tokenizer, TokenSpec, Token
from funcparserlib.parser import tok, Parser, many, forward_decl, finished, maybe
from funcparserlib.util import pretty_tree
from dataclasses import dataclass
import sys

def tokenize(s: str) -> List[Token]:
     specs = [
         TokenSpec("float", r"[+\-]?\d+\.\d*([Ee][+\-]?\d+)*"),
         TokenSpec("float", r"\d+"),
         TokenSpec("relation",r"\.\w+"),
         TokenSpec("target", r":\w+"),
         TokenSpec("inverse_relation", r"'\w+"),
         TokenSpec("idea",r"\w+"),
         TokenSpec("whitespace", r"\s+"),
         TokenSpec("or", r"\|"),
         TokenSpec("and", r"&"),
         TokenSpec("addqty", r"\+="),
         TokenSpec("minusqty", r"\-="),
         TokenSpec("timesqty", r"\*="),
         TokenSpec("divideqty", r"/="),
         TokenSpec("modqty", r"%="),
         TokenSpec("expqty", r'\^='),
     ]
     tokenizer = make_tokenizer(specs)
     return [t for t in tokenizer(s) if t.type != "whitespace"]

@dataclass
class RelationalExpr:
    idea: str | None
    relation: str | None
    target: str | None

@dataclass
class MathExpr:
     op: str
     val: str
     
@dataclass
class RelationalMathExpr:
     relExpr: RelationalExpr
     mathExpr: MathExpr
     
@dataclass
class DisjunctionExpr:
     left: RelationalExpr
     right: 'QueryExpr'

@dataclass
class ConjunctionExpr:
     left: RelationalExpr
     right: 'QueryExpr'

QueryExpr = Union[RelationalExpr, DisjunctionExpr, ConjunctionExpr, RelationalMathExpr]

def parse(tokens: List[Token]) -> QueryExpr:
    idea = tok('idea')
    relation = tok('relation') >> (lambda a: a[1:])
    target = tok('target') >> (lambda a: a[1:])
    inverse_relation = tok('inverse_relation') >> (lambda a: a[1:])

    expr = forward_decl()
    relationalExpr = \
        idea + relation + target >> (lambda args: RelationalExpr(*args)) | \
        idea + relation >> (lambda args: RelationalExpr(idea=args[0], relation=args[1], target=None)) | \
        idea + target >> (lambda args: RelationalExpr(idea=args[0], relation=None,target=args[1])) | \
        idea + inverse_relation + target >> (lambda args: RelationalExpr(idea=args[2], relation=args[1], target=args[0])) | \
        idea + inverse_relation >> (lambda args: RelationalExpr(idea=None, relation=args[1], target=args[0])) | \
        relation + target >> (lambda args: RelationalExpr(idea=None, relation=args[0], target=args[1])) | \
        idea >> (lambda i: RelationalExpr(idea=i, relation=None, target=None)) | \
        relation >> (lambda r: RelationalExpr(idea=None, relation=r,  target=None)) | \
        target >> (lambda t: RelationalExpr(idea=None, relation=None, target=t))
    mathOp = tok('addqty') | tok('minusqty') | tok('timesqty') | tok('divideqty') | tok('modqty') | tok('expqty')    
    mathExpr = mathOp + tok('float') >> (lambda args: MathExpr(op=args[0], val=args[1]))
    relationalMathExpr = relationalExpr + mathExpr >> (lambda args: RelationalMathExpr(relExpr=args[0], mathExpr=args[1]))
    term = relationalMathExpr | relationalExpr 
    disjunctionExpr = term + tok('or') + expr >> (lambda args: DisjunctionExpr(left=args[0], right=args[2]))
    conjunctionExpr = term + tok('and') + expr >> (lambda args: ConjunctionExpr(left=args[0], right=args[2]))
    expr.define(disjunctionExpr | conjunctionExpr | term)

    document = expr + -finished
    return document.parse(tokens)

def intersperse(value, seq):
    res = [value] * (2 * len(seq) - 1)
    res[::2] = seq
    return res

def compile_sql(q: QueryExpr, argc: int=1) -> Tuple[str,List[str]]:
    arg_stack = []
    sql = 'SELECT * FROM meme.meme WHERE '
    filters = []
    if isinstance(q, RelationalExpr):
        if q.idea is not None:
            filters.append(f'aid=${argc}')
            argc += 1
            arg_stack.append(q.idea)
        if q.relation is not None:
            filters.append(f'rid=${argc}')
            argc += 1
            arg_stack.append(q.relation)
        if q.target is not None:
            filters.append(f'bid=${argc}')
            argc += 1
            arg_stack.append(q.target)
    elif isinstance(q, RelationalMathExpr):
         (basesql, baseparams) = compile_sql(q.relExpr, argc)
         math_projection = compile_math_sql(q.mathExpr)
         sql = basesql.replace('*', f'aid,rid,bid,{math_projection} AS qnt', 1)
         arg_stack = baseparams
    elif isinstance(q, DisjunctionExpr):
         (left_sql, left_params) = compile_sql(q.left, argc)
         (right_sql, right_params) = compile_sql(q.right, argc + len(left_params))
         sql = f'{left_sql} UNION {right_sql}'
         arg_stack.extend(left_params + right_params)
    elif isinstance(q, ConjunctionExpr):
         (left_sql, left_params) = compile_sql(q.left, argc)
         (right_sql, right_params) = compile_sql(q.right, argc + len(left_params))
         filters.append(f'EXISTS ({left_sql}) AND EXISTS ({right_sql})')
         arg_stack.extend(left_params + right_params)
    else:
       raise ValueError(f'unknown parse value: {q}')
    sql += ' '.join(intersperse("AND", filters))
    return (sql, arg_stack)

def compile_math_sql(expr: MathExpr) -> str:
     if expr.op == '+=':
          return f'qnt + {expr.val}'
     elif expr.op == '-=':
          return f'qnt - {expr.val}'
     elif expr.op == '*=':
          return f'qnt * {expr.val}'
     elif expr.op == '/=':
          return f'qnt / {expr.val}'
     elif expr.op == '%=':
          return f'qnt % {expr.val}'
     elif expr.op == '^=':
          return f'qnt ^ {expr.val}'
     else:
          raise ValueError(f'invalid operator: {expr.op}')
    
def execute_memelang():
     (sql, params) = compile_sql(parse(tokenize(memelang_in)))
     plpy.info(sql)
     plan = plpy.prepare(sql, ['text'] * len(params))
     result = plpy.execute(plan, params)
     #for r in result:
     #     plpy.info(r)
     return [r for r in result]

