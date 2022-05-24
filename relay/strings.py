from pathlib import Path
from typing import Any, Dict, Optional
import rtoml


class StringsException(Exception):
    """
    A custom exception object for strings.
    """
    def __init__(self, message):
        self.message = message
        super(StringsException, self).__init__(message) 


class StringsStore:
    def __init__(self, 
        strings : Dict[str, Any], 
        language : str, base : "Strings",
        metadata : Optional[Dict[str, Any]] = None
    ) -> None:
        self.strings : Dict[str, Any] = strings
        self.language : str = language
        self.manager : "Strings" = base
        self.metadata : Dict[str, Any] = metadata or {}


    def get(self, tag : str, *args, **kwargs) -> Any:
        """
        Returns the string by its key.
        """
        first, *paths = tag.split(".")
        if first not in self.strings:
            raise StringsException("There is no key named \"{0}\" in \"{1}\"".format(first, tag))
        data = self.strings.get(first)
        if paths:
            for i in range(0, len(paths)):
                if paths[i] in data:
                    data = data[paths[i]]
                else:
                    raise StringsException("There is no key named \"{0}\" in \"{1}\"".format(paths[i], tag))
        return data if not isinstance(data, str) else data.format(*args, **kwargs)


    # If StringsStore object used for getting item,
    # get the string in the strings dictionary.
    #
    # _ = StringsStore(...)
    # _["greetings"]
    def __getitem__(self, key) -> Any:
        if isinstance(key, str):
            return self.get(key)
        else:
            raise StringsException("Invalid type of key. Keys must be str")
    
    # Return the language code if object is converted to a string.
    #
    # _ = StringsStore(...)
    # str(_)
    def __str__(self) -> str:
        return self.language

    # If the StringsStore object has called directly,
    # get the string in the strings dictionary.
    #
    # _ = StringsStore(...)
    # _("grettings")
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if len(args) > 0:
            return self.get(args[0], *args[1:], **kwds)
        else:
            raise StringsException("The key did not specified.")
    
    # If the StringsStore object used in "contains" operators,
    # it check if the value is in the strings dictionary.
    #
    # _ = StringsStore(...)
    # if "greetings" in _:
    #   ... 
    def __contains__(self, value) -> bool:
        return value in self.strings


class Strings:
    def __init__(self, path : Path, default : Optional[str] = None) -> None:
        self._path = path
        self._strings : Dict[str, StringsStore] = {}
        self._default : Optional[str] = default
        self._load()

    def get(self, language : str) -> StringsStore:
        return self._strings.get(language, self._strings[self._default])

    def __getitem__(self, key) -> StringsStore:
        if isinstance(key, str):
            return self.get(key)
        else:
            raise StringsException("Invalid type of key. Keys must be str")

    def _load(self) -> None:
        first = None
        for p in self._path.glob("*"):
            if not p.is_dir():
                continue
            code = p.name
            if not first:
                first = code
            defnt = None
            strings = {}
            for s in p.glob("*.toml"):
                if s.name == "_def.toml":
                    defnt = rtoml.load(s)
                else:
                    strings.update(rtoml.load(s).get("strings", {}))
            # Check if path contains definition file.
            if defnt == None:
                print(f"[STRINGS] Skipping loading '{code}', no definition file.")
                continue
            # Parse definition file.
            self._strings[code] = StringsStore(
                strings = strings,
                language = code,
                base = self,
                metadata = defnt
            )
            print(f"[STRINGS] Loaded '{code}'.")
            if not self._default:
                print(f"[STRINGS] '{code}' is now the default language.")
                self._default = code
        if not first:
            print("[STRINGS] Not loaded any strings.")
        elif self._default not in self._strings:
            print(f"[STRINGS] Default language doesn't exists, default is now '{first}'")
            self._default = first