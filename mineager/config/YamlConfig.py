#
# Copyright (C) 2020 Prof_Bloodstone.
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
from typing import List

import yaml

from mineager.plugins import Plugin

from . import Config

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader


class YamlConfig(Config):
    def _load(self) -> List[Plugin]:
        with self._file.open("r") as stream:
            return yaml.load(stream, Loader=Loader)

    def save(self) -> None:
        dump = yaml.dump(
            self.data,
            Dumper=Dumper,
            # Always use block-styled instead of collection-styled dump
            default_flow_style=False,
        )
        with self._file.open("w") as f:
            f.write(dump)
