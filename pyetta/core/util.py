import csv
from abc import abstractmethod, ABC
from typing import Dict, TypeVar, Generic

_T = TypeVar("_T")

def creation_string_to_dict(creation_string: str) -> Dict[str, str]:
    try:
        out_dictionary = dict()
        kvpairs = next(csv.reader([creation_string]))
        for kvpair in kvpairs:
            kvpair_split = next(csv.reader([kvpair], delimiter="="))
            out_dictionary[kvpair_split[0]] = kvpair_split[1]
    except Exception as ec:
        raise ValueError(f"Invalid creation string. {creation_string}") from ec
    return out_dictionary


class ICreatable(ABC, Generic[_T]):

    @classmethod
    @abstractmethod
    def from_string(cls, creation_sting, *args, **kwargs) -> _T:
        pass
