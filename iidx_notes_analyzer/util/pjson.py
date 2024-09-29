from abc import ABC, abstractmethod
import json
from typing import Any, Iterable, TextIO

# 基本型以外（独自クラスとか）は対応していない。
# TODO: バリデート

class _Config:
    def __init__(self, width: int, indent: int, ensure_ascii: bool) -> None:
        if indent < 0:
            raise ValueError(indent)

        self._width = width
        self._indent = indent
        self._ensure_ascii = ensure_ascii

    @property
    def width(self) -> int:
        return self._width

    @property
    def indent(self) -> int:
        return self._indent

    @property
    def ensure_ascii(self) -> bool:
        return self._ensure_ascii

class _JSONChunksGenerator(ABC):
    def __init__(self, config: _Config) -> None:
        super().__init__()
        self._config = config

    @abstractmethod
    def size_of_one_line(self) -> int:
        pass

    @abstractmethod
    def one_line(self) -> Iterable[str]:
        pass

    @abstractmethod
    def pretty(self, indent_level: int = 0) -> Iterable[str]:
        pass

class _JSONChunksGeneratorAtomic(_JSONChunksGenerator):
    def __init__(
        self, config: _Config,
        obj: Any,
    ) -> None:
        super().__init__(config)
        self._text = json.dumps(obj, ensure_ascii=config.ensure_ascii)

    def size_of_one_line(self) -> int:
        return len(self._text)

    def one_line(self) -> Iterable[str]:
        yield self._text

    def pretty(self, indent_level: int = 0) -> Iterable[str]:
        return self.one_line()

class _JSONChunksGeneratorArray(_JSONChunksGenerator):
    def __init__(
        self, config: _Config,
        children: list[_JSONChunksGenerator],
    ) -> None:
        super().__init__(config)
        self._children = children

    def size_of_one_line(self) -> int:
        return len('[') +\
            sum(child.size_of_one_line() for child in self._children) +\
            len(',') * (max(len(self._children) - 1, 0)) +\
            len(']')

    def one_line(self) -> Iterable[str]:
        yield '['
        for i, child in enumerate(self._children):
            yield from child.one_line()
            if i < len(self._children) - 1:
                yield ','
        yield ']'

    def pretty(self, indent_level: int = 0) -> Iterable[str]:
        # TODO: 行内での開始位置を考慮してない
        if self.size_of_one_line() <= self._config.width:
            yield from self.one_line()
            return

        yield '[\n'
        for i, child in enumerate(self._children):
            yield ' ' * self._config.indent * (indent_level + 1)
            yield from child.pretty(indent_level + 1)
            if i < len(self._children) - 1:
                yield ','
            yield '\n'
        yield ' ' * self._config.indent * indent_level
        yield ']'

class _JSONChunksGeneratorObject(_JSONChunksGenerator):
    def __init__(
        self, config: _Config,
        children: dict[str, _JSONChunksGenerator],
    ) -> None:
        super().__init__(config)
        self._children = children

    def size_of_one_line(self) -> int:
        return len('{') +\
            sum(
                len('"') + len(key) + len('"') + len(':') + child.size_of_one_line()
                for key, child in self._children.items()
            ) +\
            len(',') * (max(len(self._children) - 1, 0)) +\
            len('}')

    def one_line(self) -> Iterable[str]:
        yield '{'
        for i, (key, child) in enumerate(self._children.items()):
            yield from ('"', key, '"')
            yield ':'
            yield from child.one_line()
            if i < len(self._children) - 1:
                yield ','
        yield '}'

    def pretty(self, indent_level: int = 0) -> Iterable[str]:
        # TODO: 行内での開始位置を考慮してない
        if self.size_of_one_line() <= self._config.width:
            yield from self.one_line()
            return

        yield '{\n'
        for i, (key, child) in enumerate(self._children.items()):
            yield ' ' * self._config.indent * (indent_level + 1)
            yield from ('"', key, '"')
            yield ': '
            yield from child.pretty(indent_level + 1)
            if i < len(self._children) - 1:
                yield ','
            yield '\n'
        yield ' ' * self._config.indent * indent_level
        yield '}'

def _make_generator(config: _Config, obj: Any) -> _JSONChunksGenerator:
    if isinstance(obj, dict):
        return _JSONChunksGeneratorObject(config, {
            k: _make_generator(config, v) for k, v in obj.items()
        })
    if isinstance(obj, list) or isinstance(obj, tuple):
        return _JSONChunksGeneratorArray(config, [
            _make_generator(config, e) for e in obj
        ])
    return _JSONChunksGeneratorAtomic(config, obj)

def dump(
    obj: Any, fp: TextIO,
    width: int = 80, indent: int = 2, ensure_ascii: bool = True,
) -> None:
    config = _Config(width, indent, ensure_ascii)
    gen = _make_generator(config, obj)
    for chunk in gen.pretty():
        fp.write(chunk)

def dumps(
    obj: Any,
    width: int = 80, indent: int = 2, ensure_ascii: bool = True,
) -> str:
    config = _Config(width, indent, ensure_ascii)
    gen = _make_generator(config, obj)
    return ''.join(gen.pretty())
