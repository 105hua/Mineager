#
# Copyright (C) 2021 Prof_Bloodstone.
#
# This file is part of mineager
# (see https://github.com/Prof-Bloodstone/Mineager).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
import dataclasses
import enum
import io
import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union
from zipfile import ZipFile

import yaml
from requests import Session

from mineager import utils
from mineager.globals import SESSION

from ..utils import get_function_kwargs


@dataclasses.dataclass(frozen=True)
class PluginPlatformInfo:
    config_file: str
    loader: Callable[[io.TextIOBase], Any]


@enum.unique
class PluginPlatform(enum.Enum):
    PAPER = PluginPlatformInfo("plugin.yml", yaml.safe_load)
    VELOCITY = PluginPlatformInfo("velocity-plugin.json", json.load)


class Version:
    def __init__(self, name: str, version: str, date: datetime):
        self.name = name
        self.version = version
        self.date = date

    @classmethod
    def from_timestamp(cls, name: str, version: str, date: int, *args, **kwargs):
        return cls(name, version, datetime.fromtimestamp(date), *args, **kwargs)

    def as_tuple(self) -> tuple:
        return self.name, self.version, self.date

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name},version={self.version},date={self.date})"

    @staticmethod
    def __is_valid_operand(other):
        required_attributes = (
            "name",
            "version",
        )
        return all(hasattr(other, attribute) for attribute in required_attributes)

    def __eq__(self, other):
        if not self.__is_valid_operand(other):
            return NotImplemented
        return (self.name, self.version) == (other.name, other.version)

    def __lt__(self, other):
        # Casefold both vars before comparison.
        cased_self = self.name.casefold()
        cased_other = other.name.casefold()
        if not self.__is_valid_operand(other):
            return NotImplemented
        if cased_self != cased_other:
            print("WARNING: Self Version is not equal to Other Version!")
            print(f"Self name: {cased_self}")
            print(f"Other name: {cased_other}")
        if not hasattr(other, "date"):
            return NotImplemented
        # TODO: Compare versions if they are SEMVER?
        return self.date < other.date


class Plugin(ABC):

    type: str = NotImplemented
    _session: Session = SESSION

    def __init__(
        self, name: str, resource: Union[str, int], prefix: Optional[str] = None
    ):
        self.name = name
        self._resource = resource
        self.prefix = prefix
        self.__latest_version = None

    def normalize_name(self):
        self.name = self.name.replace("-_", " ").title()

    def serialize(self) -> Dict[str, Any]:
        fields = get_function_kwargs(self.__init__)
        return {name: getattr(self, name) for name in fields}

    def __repr__(self) -> str:
        representation = f"{type(self).__qualname__}("
        for idx, (name, value) in enumerate(self.serialize().items()):
            representation = (
                f"{representation}{', ' if idx != 0 else ''}{name}={value!r}"
            )
        return f"{representation})"

    def clear_cache(self):
        self.__latest_version = None

    def _get(self, url: str, *args, **kwargs):
        return self._session.get(url, *args, **kwargs)

    @property
    def default_file_path(self) -> Path:
        return Path(f'./plugins/{self.name.replace(" -", "_")}.jar')

    @abstractmethod
    def get_latest_version_info(self) -> Version:
        pass

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        if "/" in name:
            raise ValueError(f"{name!r} contains invalid character - '/'")
        self._name = name

    @property
    def resource(self):
        return self._resource

    @property
    def prefix(self) -> str:
        return self._prefix or self.name

    @prefix.setter
    def prefix(self, prefix: Optional[str]):
        self._prefix = prefix

    @property
    def latest_version(self):
        if self.__latest_version is None:
            self.__latest_version = self.get_latest_version_info()
        return self.__latest_version

    def get_platform(self, file: Path) -> PluginPlatform:
        if file is None:
            file = self.default_file_path
        if not file.exists():
            return None

        with ZipFile(file) as zipfile:
            for platform in PluginPlatform:
                try:
                    zipfile.getinfo(platform.value.config_file)
                    return platform
                except KeyError:
                    pass
            raise NotAPluginException(f"{file} doesn't have plugin configs!")

    def version_from_file(self, file: Path = None) -> Union[Version, None]:
        if file is None:
            file = self.default_file_path
        if not file.exists():
            return None

        platform = self.get_platform(file)

        with ZipFile(file) as zipfile:
            # date = datetime(*zipinfo.date_time)

            with zipfile.open(platform.value.config_file) as plug:
                data = platform.value.loader(plug)
            version = data["version"]
            return Version.from_timestamp(
                name=file.stem, version=version, date=int(file.stat().st_mtime)
            )

    def _download(self, version: Version, file: Path) -> None:
        url = self.download_url(version)
        response = self._get(url)
        if not response.ok and response.headers.get("server") == "cloudflare":
            raise ManualDownloadRequired("Cloudflare blocked automatic download.", url)
        response.raise_for_status()
        utils.response_to_file(response, file)

    def download(self, version: Version = None, file: Path = None) -> None:
        if version is None:
            version = self.latest_version
        if file is None:
            file = self.default_file_path
        self._download(version, file)

    @abstractmethod
    def download_url(self, version: Version) -> str:
        pass


class ManualDownloadRequired(Exception):
    def __init__(self, msg: str, url: str):
        self._raw_msg = msg
        self.url = url
        self._msg = f"{msg} {url}"
        super().__init__(self._msg)


class NotAPluginException(Exception):
    pass


class InvalidPluginSourceException(Exception):
    pass
