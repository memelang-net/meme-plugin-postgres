from typing import List, Tuple, Union
from funcparserlib.lexer import make_tokenizer, TokenSpec, Token
from funcparserlib.parser import tok, Parser, many, forward_decl, finished
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

QueryExpr = Union[Relation,Idea,InverseRelation]

def parse(tokens: List[Token]) -> QueryExpr:
    idea = tok('idea') >> (lambda a: Idea(a[0]))
    relation = tok('relation') >> (lambda a: Relation(a[0][1:]))
    document = (idea | relation) + -finished
    return document.parse(tokens)