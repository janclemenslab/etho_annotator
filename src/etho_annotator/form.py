import yaml
from typing import Any, IO, Dict
import os
from collections import defaultdict


def dot_keys_to_nested(data: Dict) -> Dict:
    """old['aaaa.bbbb'] -> d['aaaa']['bbbb']

    Args:
        data (Dict): [description]

    Returns:
        Dict: [description]
    """
    rules = defaultdict(lambda: dict())
    for key, val in data.items():
        if "." in key:
            key, _, param = key.partition(".")
            rules[key][param] = val
        else:
            rules[key] = val
    return rules


def nested_to_dot_keys(data: Dict) -> Dict:
    """old['aaaa']['bbbb'] -> d['aaaa.bbbb']

    Args:
        data (Dict): [description]

    Returns:
        Dict: [description]
    """
    rules = defaultdict(lambda: dict())
    for key, val in data.items():
        if isinstance(val, dict):
            for key2, val2 in val.items():
                rules[f"{key}.{key2}"] = val2
        else:
            rules[key] = val
    return rules


class Loader(yaml.SafeLoader):
    """YAML Loader with `!include` constructor."""

    def __init__(self, stream: IO) -> None:
        """Initialise Loader."""

        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream)


def construct_include(loader: Loader, node: yaml.Node) -> Any:
    """Include file referenced at node."""

    filename = os.path.abspath(
        os.path.join(loader._root, loader.construct_scalar(node))
    )
    extension = os.path.splitext(filename)[1].lstrip(".")

    with open(filename, "r") as f:
        if extension in ("yaml", "yml"):
            return yaml.load(f, Loader)
        else:
            return "".join(f.readlines())


yaml.add_constructor("!include", construct_include, Loader)
