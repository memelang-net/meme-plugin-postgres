from typing import List, Tuple, Union
from funcparserlib.lexer import make_tokenizer, TokenSpec, Token
from funcparserlib.parser import tok, Parser, many, forward_decl, finished, maybe
from funcparserlib.util import pretty_tree
from dataclasses import dataclass

def tokenize(s: str) -> List[Token]:
     specs = [
         TokenSpec("relation",r"\.\w+"),
         TokenSpec("target", r":\w+"),
         TokenSpec("inverse_relation", r"'\w+"),
         TokenSpec("idea",r"\w+"),
         TokenSpec("whitespace", r"\s+"),
         TokenSpec("or", r"\|"),
         TokenSpec("and", r"&"),
     ]
     tokenizer = make_tokenizer(specs)
     return [t for t in tokenizer(s) if t.type != "whitespace"]


@dataclass
class Relation:
    name: str

@dataclass
class InverseRelation:
    name: str

@dataclass
class Idea:
    name: str

@dataclass
class Target:
    name: str

@dataclass
class Apply:
    left: any
    right: any

@dataclass
class RelationalExpr:
    idea: str
    relation: str
    target: str

QueryExpr = Union[Relation,Idea,InverseRelation]

def parse(tokens: List[Token]) -> QueryExpr:
    idea = tok('idea')
    relation = tok('relation') >> (lambda a: a[1:])
    target = tok('target') >> (lambda a: a[1:])
    inverse_relation = tok('inverse_relation') >> (lambda a: a[1:])

    relationalExpr = \
        idea + relation + target >> (lambda args: RelationalExpr(*args)) | \
        idea + relation >> (lambda args: RelationalExpr(target=None, *args)) | \
        idea + target >> (lambda args: RelationalExpr(idea=args[0], relation=None,target=args[1])) | \
        idea + inverse_relation + target >> (lambda args: RelationalExpr(idea=args[2], relation=args[1], target=args[0])) | \
        idea + inverse_relation >> (lambda args: RelationalExpr(idea=None, relation=args[1], target=args[0])) | \
        relation + target >> (lambda args: RelationalExpr(idea=None, relation=args[0], target=args[1])) | \
        idea >> (lambda i: RelationalExpr(idea=i, relation=None, target=None)) | \
        relation >> (lambda r: RelationalExpr(idea=None, relation=r,  target=None)) | \
        target >> (lambda t: RelationalExpr(idea=None, relation=None, target=t))

    document = relationalExpr + -finished
    return document.parse(tokens)

def intersperse(value, seq):
    res = [value] * (2 * len(seq) - 1)
    res[::2] = seq
    return res

def compile_sql(q: QueryExpr) -> Tuple[str,List[str]]:
    arg_stack = []
    sql = 'SELECT * FROM mem WHERE '
    filters = []
    argc = 1
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
    sql += ' '.join(intersperse("AND", filters))
    return (sql, arg_stack)
    
