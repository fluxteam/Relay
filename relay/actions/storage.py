from typing import Any
from hikari import Guild
from relay.database import MongoDB
from pyconduit import Category
from pyconduit import block
from hikari import UNDEFINED

# STORAGE
# Write and read values from database.
class Storage(Category):
    """
    Persistent storage for Relay Actions. Refer to [Relay Actions](../actions) to learn how to use them.
    """

    @block()
    @staticmethod
    def write(
        db__ : MongoDB, 
        guild__ : Guild, 
        *,
        key : str, 
        value : Any
    ) -> None:
        """
        Writes a custom data in the current server's storage.
        """
        db__("relay-actions", "storage", guild__.id).write({key : value})


    @block()
    @staticmethod
    def read(
        db__ : MongoDB, 
        guild__ : Guild, 
        *, 
        key : str,
        default : Any = UNDEFINED
    ) -> Any:
        """
        Reads a value in the current server's storage. If key doesn't exists and `default` has provided, 
        returns default, otherwise raises error.
        """
        if default != UNDEFINED:
            return db__("relay-actions", "storage", guild__.id).read(projection = [key]).get(key, default)
        else:
            return db__("relay-actions", "storage", guild__.id).read(projection = [key])[key]

    
    @block()
    @staticmethod
    def exists(
        db__ : MongoDB, 
        guild__ : Guild, 
        *,
        key : str
    ) -> bool:
        """
        Check if key exists.
        """
        return key in db__("relay-actions", "storage", guild__.id).read(projection = [key])

    
    @block()
    @staticmethod
    def exists_assert(
        db__ : MongoDB, 
        guild__ : Guild, 
        *,
        key : str
    ) -> None:
        """
        Check if key exists. If the key doesn't exists, raises an error instead of returning `False`.
        """
        s = key in db__("relay-actions", "storage", guild__.id).read(projection = ["_id"])
        if s:
            pass
        else:
            raise ValueError(key)