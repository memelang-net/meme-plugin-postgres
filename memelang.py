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

QueryExpr = Union[Relation,Idea,InverseRelation]

def parse(tokens: List[Token]) -> QueryExpr:
    idea = tok('idea') >> (lambda a: Idea(a))
    relation = tok('relation') >> (lambda a: Relation(a[1:]))
    target = tok('target') >> (lambda a: Target(a[1:]))
    inverse_relation = tok('inverse_relation') >> (lambda a: InverseRelation(a[1:]))
    chain = forward_decl()
    def chains(args):
        return Apply(left=args[0], right=args[1])
    chain.define((idea | relation | inverse_relation | target) + maybe(chain) >> chains)
    document = chain + -finished
    return document.parse(tokens)