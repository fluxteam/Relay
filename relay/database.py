"""
A simple wrapper for MongoClient.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


LEVEL_INVALID    = 0
LEVEL_CLIENT     = 1
LEVEL_DATABASE   = 2
LEVEL_COLLECTION = 3
LEVEL_DOCUMENT   = 4


class MongoDBClient:
    _created : Optional["MongoDB"] = None

    @staticmethod
    def create(url : str, mkdocs : bool) -> MongoClient:
        if mkdocs:
            return None
        return MongoClient(url, connect = True)

    @classmethod
    def get(cls, url : str, mkdocs : bool) -> "MongoDB":
        if cls._created:
            return cls._created
        cls._created = MongoDB(client = cls.create(url, mkdocs))
        return cls._created


class MongoDB:
    """
    A simple wrapper for MongoClient.
    """

    def __init__(
        self, 
        client : MongoClient, 
        reference : Union[Database, Collection, None] = None,
        document : Optional[str] = None
    ) -> None:
        self._client : MongoClient = client
        self._reference : Union[Database, MongoClient, Collection] = reference or self._client
        self._document : Optional[str] = document
        self._level : int = LEVEL_INVALID
        self._refresh_level()


    def _refresh_level(self) -> None:
        if isinstance(self._reference, MongoClient):
            self._level = LEVEL_CLIENT
        elif isinstance(self._reference, Database):
            self._level = LEVEL_DATABASE
        elif isinstance(self._reference, Collection):
            if self._document:
                self._level = LEVEL_DOCUMENT
            else:
                self._level = LEVEL_COLLECTION
        else:
            self._level = LEVEL_INVALID

    
    def _error_invalid_level(self, accepted : Optional[List[int]] = None) -> None:
        if self._level in accepted:
            return
        raise ValueError(
            "Invalid level for this operation. " +
            ("" if not accepted else f"The current level is {self._level} but required {accepted}")
        )

    
    @staticmethod
    def _sep_operators(data, key : Optional[str] = None) -> Dict[str, Any]:
        d = {key: {}} if key else {}
        for k, v in data.items():
            if k.startswith("$"):
                d[k] = v
            else:
                if key:
                    d[key][k] = v
                else:
                    d[k] = v
        return d

    
    # Switches the context between collections and databases.
    # To access a location in MongoDB, use attributes or calls.
    def __go_down__(self, name : str) -> None:
        if self._level == LEVEL_INVALID:
            raise TypeError("Reference is invalid.")
        elif self._level == LEVEL_CLIENT:
            self._reference = self._reference[name]
        elif self._level == LEVEL_DATABASE:
            self._reference = self._reference[name]
        elif self._level == LEVEL_COLLECTION:
            self._document = name
        elif self._level == LEVEL_DOCUMENT:
            raise TypeError("Can't go further than a document.")
        self._refresh_level()

    
    def __go_up__(self) -> None:
        if self._level == LEVEL_INVALID:
            raise TypeError("Reference is invalid.")
        elif self._level == LEVEL_CLIENT:
            raise TypeError("Can't go upper than a client.")
        elif self._level == LEVEL_DATABASE:
            self._reference = self._reference.client
        elif self._level == LEVEL_COLLECTION:
            self._reference = self._reference.database
        elif self._level == LEVEL_DOCUMENT:
            self._document = None
        self._refresh_level()
    
    
    # Switches the context between collections and databases.
    # To access a location in MongoDB, use attributes or calls.
    def go(self, *args: Any, start_from_root : bool = False, upper : bool = False) -> "MongoDB":
        """
        Switches the context between collections and databases.
        To access a location in MongoDB, use attributes or calls.

        To change the path from root instead of from the current path, set `start_from_root` to `True`.
        """
        if not args:
            return self
        if len(args) > LEVEL_COLLECTION:
            raise ValueError("Can't go further/upper than a document.")
        x = MongoDB(self._client, None if start_from_root else self._reference, self._document)
        for item in args:
            if item != None:
                if upper:
                    x.__go_up__(str(item))
                else:
                    x.__go_down__(str(item))
        return x


    def read(self, query = None, *args, **kwargs) -> Dict[str, Any]:
        """
        Gets the value from MongoDB.
        """
        if self._level == LEVEL_DOCUMENT:
            return (self._reference.find_one({"_id": self._document}, *args, **kwargs) or {})
        if self._level == LEVEL_COLLECTION:
            return {x["_id"] : x for x in self._reference.find(query or {}, *args, **kwargs)}
        self._error_invalid_level([LEVEL_DOCUMENT])

    
    def write(self, data : dict, /, query = None, approve : bool = False, overwrite = False) -> None:
        """
        Writes a value to MongoDB.
        """
        if self._level == LEVEL_DOCUMENT:
            if overwrite:
                self._reference.find_one_and_replace({"_id": self._document }, data, upsert = True)
            else:
                self._reference.find_one_and_update({"_id": self._document }, self._sep_operators(data, "$set"), upsert = True)
            return
        if self._level == LEVEL_COLLECTION:
            if (not approve) and (not query):
                raise TypeError(
                    "Writing the entire collection is blocked to prevent data loss. " + \
                    "If this was intended, set 'approve' to True."
                )
            if overwrite:
                self._reference.update_many(query or {}, data, upsert = True)
            else:
                self._reference.update_many(query or {}, self._sep_operators(data, "$set"), upsert = True)
            return
        self._error_invalid_level([LEVEL_COLLECTION, LEVEL_DOCUMENT])

    
    def delete(self, /, query = None, approve : bool = False, *args, **kwargs) -> None:
        """
        Deletes a value from MongoDB.
        """
        if self._level == LEVEL_DOCUMENT:
            self._reference.delete_one({"_id": self._document}, *args, **kwargs)
            return
        if self._level == LEVEL_COLLECTION:
            if (not approve) and (not query):
                raise TypeError(
                    "Writing the entire collection is blocked to prevent data loss. " + \
                    "If this was intended, set 'approve' to True."
                )
            self._reference.delete_many(query or {}, *args, **kwargs)
            return
        self._error_invalid_level([LEVEL_COLLECTION, LEVEL_DOCUMENT])

    
    def list_items(self, **kwargs) -> List[str]:
        """
        Lists IDs in MongoDB.
        """
        if self._level == LEVEL_DOCUMENT:
            return [self._document]
        elif self._level == LEVEL_COLLECTION:
            prj = kwargs.pop("projection", ["_id"])
            return [x["_id"] for x in self._reference.find({}, projection = prj, **kwargs)]
        elif self._level == LEVEL_DATABASE:
            return self._reference.list_collection_names(**kwargs)
        elif self._level == LEVEL_CLIENT:
            return self._reference.list_database_names()
    

    # Gets the ID.
    @property
    def id(self) -> str:
        if self._level == LEVEL_CLIENT:
            return ""
        elif self._level == LEVEL_DATABASE:
            return self._reference.name
        elif self._level == LEVEL_COLLECTION:
            return self._reference.name
        elif self._level == LEVEL_DOCUMENT:
            return self._document

    
    # Gets the path of the object.
    @property
    def path(self) -> Tuple[str]:
        if self._level == LEVEL_CLIENT:
            return ()
        elif self._level == LEVEL_DATABASE:
            return (self._reference.name)
        elif self._level == LEVEL_COLLECTION:
            return (self._reference.database.name, self._reference.name)
        elif self._level == LEVEL_DOCUMENT:
            return (self._reference.database.name, self._reference.name, self._document)

    
    @property
    def exists(self) -> bool:
        if self._level == LEVEL_DOCUMENT:
            return bool(self.read(projection = ["_id"]).get("_id"))
        elif self._level == LEVEL_COLLECTION:
            return bool(self._reference.database.list_collection_names(filter = {"name": self._reference.name}))
        elif self._level == LEVEL_DATABASE:
            return self._reference.name in self._client.list_database_names()
        elif self._level == LEVEL_CLIENT:
            return True
        return False


    def __call__(self, *args: Any, **kwargs: Any) -> "MongoDB":
        return self.go(*args, **kwargs)