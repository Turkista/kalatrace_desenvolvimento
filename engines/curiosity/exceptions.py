class CuriosityException(Exception):
    """Base Exception."""


class GraphUnavailable(CuriosityException):
    """Knowledge Graph unavailable."""


class InvalidNode(CuriosityException):
    """Node not found."""


class EmptyKnowledgeBase(CuriosityException):
    """Knowledge Graph is empty."""