from datetime import datetime
from .Plugin import Plugin, Version, InvalidPluginSourceException

class ModrinthVersion(Version):
    def __init__(self, name: str, version: str, date: datetime, download_url: str):
        split_name = name.split("/")
        super().__init__(name=split_name[0], version=version, date=date)
        self.download_url=download_url

class ModrinthPlugin(Plugin):
    _base_url = "https://api.modrinth.com/v2/project"
    type = "modrinth"
    def get_latest_version_info(self):
        url = f"{self._base_url}/{self.name}/version"
        response = self._get(url)
        response.raise_for_status()
        json = response.json()
        for version in json:
            if "paper" in version["loaders"]:
                return ModrinthVersion(
                    name=version["name"],
                    version=version["version_number"],
                    date=version["date_published"],
                    download_url=version["files"][0]["url"]
                )
        raise InvalidPluginSourceException(f"Looks like {self.name} doesn't have any paper builds!")
    
    def download_url(self, version: ModrinthVersion) -> str:
        return version.download_url