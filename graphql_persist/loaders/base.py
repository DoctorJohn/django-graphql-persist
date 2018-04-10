from django.utils.functional import cached_property

from graphql.language.parser import parse
from graphql.language.printer import print_ast
from graphql.language.source import Source

from .exceptions import DocumentDoesNotExist
from .parser import parse_document


class Origin:

    def __init__(self, name, query_key, loader):
        self.name = name
        self.query_key = query_key
        self.loader = loader

    def __str__(self):
        return self.name


class Document:

    def __init__(self, source, origin=None):
        self.source = Source(source)
        self.origin = origin
        self.ast = parse(self.source)

    def render(self):
        return parse_document(self)

    @cached_property
    def definitions(self):
        self.ast = parse(self.render())
        return {
            definition.name.value: print_ast(definition)
            for definition in self.ast.definitions
        }


class BaseLoader:

    def __init__(self, engine):
        self.engine = engine

    def get_document(self, query_key):
        for origin in self.get_sources(query_key):
            try:
                contents = self.get_contents(origin)
            except DocumentDoesNotExist:
                continue
            return Document(source=contents, origin=origin)
        raise DocumentDoesNotExist(query_key)

    def get_sources(self, query_key):
        raise NotImplementedError('.get_sources() must be implemented')

    def get_contents(self, origin):
        raise NotImplementedError('.get_contents() must be implemented')
