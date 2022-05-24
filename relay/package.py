__all__ = [
    "RelayPackage", 
    "RelayPackageManager", 
    "RelayPartialPackage"
]

from relay_packages import Package, PackageArchive
from relay_packages.raw import PackageSource
from relay.commons import marketplace, snowflaked, db
from relay.utils import make_run
from typing import (
    Dict,
    Any,
    Optional,
    Union
)


class RelayPackageManager:
    """
    Manages RelayPackages in the server.
    """
    market = marketplace

    def __init__(self, guild_id : Optional[int] = None) -> None:
        self.guild_id = guild_id
        self.packages : Dict[str, "RelayPackage"] = {}


    def fetch(self) -> None:
        """
        Lists the packages in specified server and loads it to manager.
        """
        self.packages.clear()
        if not self.guild_id:
            return
        for k, v in db("relay-actions", self.guild_id).read({"pack": {"$exists": True}}).items():
            if ("pack" in v) and ("pack_data" in v):
                pack_name = v["pack"]["name"]
                pack_version = v["pack"]["version"]
                pack_source = v["pack"].get("source", "marketplace")
                # Skip already existed packages.
                if pack_name in self.packages:
                    self.packages[pack_name].workflows[k] = v
                    continue
                # Get pack from marketplace if source is marketplace.
                if pack_source == "marketplace":
                    # Add package object if not exists.
                    p = self.market.pack(pack_name)
                    self.packages[pack_name] = RelayPackage(
                        archive = p.contents(pack_version),
                        workflows = {}
                    )
                    self.packages[pack_name].workflows[k] = v
                # Else get from package index.
                else:
                    pack_source = db("relay", "packages", pack_name).read()
                    p = self.build_user_package(pack_name, pack_source)
                    self.packages[pack_name] = RelayPackage(
                        archive = p.contents(pack_version),
                        workflows = {}
                    )
                    self.packages[pack_name].workflows[k] = v

    
    def get(
        self, 
        pack_name : str
    ) -> Optional["RelayPackage"]:
        """
        Gets a package by its name. If package has installed already 
        returns the package, otherwise returns None.
        """
        if pack_name in self.packages:
            return self.packages[pack_name]

    
    def get_or_fetch(
        self, 
        pack_name : str, 
        pack_version : str = None,
        include_user : bool = False
    ) -> Union["RelayPackage", "RelayPartialPackage", None]:
        """
        Gets a package by its name. If package has installed already 
        returns the package, otherwise creates a new RelayPartialPackage with provided pack_version.

        If package doesn't exists in the repo, returns None.
        """
        if pack_name in self.packages:
            return self.packages[pack_name]
        pack = self.market.pack(pack_name)
        if not pack:
            if include_user:
                pack_source = db("relay", "packages", pack_name).read()
                if not pack_source:
                    return
                p = self.build_user_package(pack_name, pack_source)
                ver = pack_version or p.latest_version
                if p and (ver in p.versions):
                    return RelayPartialPackage(archive = p.contents(ver))
            return
        ver = pack_version or pack.latest_version
        if pack and (ver in pack.versions):
            return RelayPartialPackage(archive = pack.contents(ver))


    def uninstall(
        self, 
        pack_name : str
    ) -> None:
        """
        Uninstalls a package. Does nothing if package has not installed.
        """
        if pack_name not in self.packages:
            return
        if not self.guild_id:
            return
        # Remove workflows.
        for workflow_id in self.packages[pack_name].workflows:
            db("relay-actions", self.guild_id, workflow_id).delete()
        del self.packages[pack_name]


    def install(
        self, 
        pack_name : str, 
        user_data : Dict[str, Any], 
        pack_version : str = None,
        install_source : bool = False
    ) -> None:
        """
        Installs a package. Does nothing if package has installed already.

        Note that this assumes all type validations has made. 
        It doesn't enforce any type validations and it doesn't raise error when there is missing required field.
        """
        if pack_name in self.packages:
            return
        # Get the package.
        partial = self.get_or_fetch(pack_name, pack_version)
        if partial == None:
            return
        # Install workflows for user packages.
        if partial.is_user_package:
            for k, v in partial.archive.workflows.items():
                db("relay-actions", self.guild_id, k).write(v.export(partial.archive), overwrite = True)
            if install_source:
                blocks = db("relay", "packages", pack_name).read(projection = ["blocks"])["blocks"]
                if blocks:
                    db("relay-actions", "workspaces", self.guild_id).write({
                        "$push": {
                            "blockly.blocks.blocks": {
                                "$each": blocks
                            }
                        }
                    })
            return
        # Install workflows for marketplace packages.
        output = partial.archive.export(user_data)
        for workflow_data in output["workflows"]:
            wid = make_run(
                "PACK",
                content = (partial.id, partial.version, ),
                event = workflow_data["event"] or "NONE",
                workflow = str(snowflaked())
            )
            if not self.guild_id:
                return
            db("relay-actions", self.guild_id, wid).write(workflow_data["workflow"], overwrite = True)
        # Create a package info object.
        self.packages[pack_name] = RelayPackage(
            archive = partial.archive,
            workflows = output["workflows"]
        )

    
    def fix(self, pack_name : str) -> None:
        """
        Fixes a package installation by uninstalling and reinstalling the package.
        Does nothing if package has not installed or/and package doesn't require fixing.
        """
        if pack_name not in self.packages:
            return
        pack = self.get(pack_name)
        if not pack.is_broken:
            return
        self.uninstall(pack_name)
        self.install(pack_name, pack.params, pack.version)
    

    def update(self, pack_name : str, user_data : Dict[str, Any]) -> None:
        """
        Updates the package with the given user parameters.
        Does nothing if package has not installed or/and package is already up to date.
        """
        if pack_name not in self.packages:
            return
        pack = self.get(pack_name)
        if pack.is_updated:
            return
        self.uninstall(pack_name)
        self.install(pack_name, user_data)


    def build_user_package(self, id : str, data : Dict[str, Any]) -> "Package":
        """
        Builds a "fake" RelayPackage from given user package format.
        """
        return Package(self.market, id, {
            "metadata": {
                "pack": {**data["pack"], "author": {"username": "user-package"}}
            },
            "versions": {
                "default": {
                    "metadata": {},
                    "workflows": data["workflows"]
                }
            }
        }, source = PackageSource(service = "github", name = id))


class RelayPartialPackage:
    """
    Holds information about a non-installed package.
    """
    def __init__(self, archive : "PackageArchive") -> None:
        self.archive = archive

    @property
    def version(self) -> str:
        return self.archive.id

    @property
    def id(self) -> str:
        return self.archive.parent.id

    @property
    def package(self) -> Package:
        return self.archive.parent

    @property
    def is_installed(self) -> bool:
        """
        Returns True if package has installed, this is always True for RelayPackages and
        False for RelayPartialPackages.
        """
        return bool(self)

    @property
    def is_user_package(self) -> bool:
        """
        Returns True if this is a user package.
        """
        return self.package.source.service == "github"

    def __repr__(self) -> str:
        return f"<RelayPartialPackage for '{self.id}' version {self.version}>"

    def __str__(self) -> str:
        return self.id

    def __bool__(self) -> bool:
        return False


class RelayPackage(RelayPartialPackage):
    """
    Holds information about a installed package.
    """
    def __init__(self, archive : "PackageArchive", workflows : Dict[str, Any]) -> None:
        super().__init__(archive)
        self.workflows : Dict[str, Any] = workflows

    @property
    def params(self) -> Dict[str, Any]:
        """
        Gets the installed parameters.
        """
        return list(self.workflows.values())[0]["pack_data"].get("parameters", {})

    @property
    def is_updated(self) -> bool:
        """
        True if package is up to date, otherwise False.
        """
        return self.package.versions[self.version] == self.package.versions[self.package.latest_version]

    @property
    def supports_direct_update(self) -> bool:
        """
        True if direct update available. False otherwise.
        Direct update means no user interaction needed to update the package.
        If the new version requires a new parameters, this means extra user interaction needed. 
        """
        if self.is_updated:
            return True
        for param in self.package.contents().parameters.values():
            # Check if a new parameter has added and installed version
            # doesn't have that parameter.
            if param.required and (param.id not in self.archive.parameters):
                return False
            # Check if a current parameter has updated its type.
            elif (param.id in self.archive.parameters) and param.type != self.archive.parameters[param.id].type:
                return False
        return True

    @property
    def is_broken(self) -> bool:
        """
        Checks if package files are broken.
        """
        return not self.archive.compare_workflows({ v["pack_data"]["workflow"] : v for v in self.workflows.values() })

    def __repr__(self) -> str:
        return f"<RelayPackage for '{self.id}' version {self.version}>"

    def __bool__(self) -> bool:
        return True