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
from typing import Iterable, Type

from .GithubPlugin import GithubPlugin
from .JenkinsPlugin import JenkinsPlugin
from .Plugin import Plugin
from .SpigetPlugin import SpigetPlugin
from .ModrinthPlugin import ModrinthPlugin

PLUGIN_CLASSES: Iterable[Type[Plugin]] = (
    SpigetPlugin,
    GithubPlugin,
    JenkinsPlugin,
    ModrinthPlugin
)


def get_plugin(name: str) -> Type[Plugin]:
    name = name.lower()
    for cls in PLUGIN_CLASSES:
        if name == cls.type:
            return cls
    raise ValueError(f"Unable to find plugin of type {name}")
