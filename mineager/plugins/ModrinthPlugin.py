from datetime import datetime

from mineager.plugins.Plugin import Version
from .Plugin import Plugin, Version, InvalidPluginSourceException

class ModrinthVersion(Version):
    def __init__(self, name: str, version: str, date: datetime, download_url: str):
        super().__init__(name=name, version=version, date=date)
        self.download_url=download_url

class ModrinthPlugin(Plugin):
    _base_url = "https://api.modrinth.com/v2/project"
    _datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    type = "modrinth"
    def get_latest_version_info(self):
        # Get Project Information
        project_url = f"{self._base_url}/{self.name}"
        project_response = self._get(project_url)
        project_response.raise_for_status()
        project_json = project_response.json()
        # Get Latest Version Information
        version_url = f"{project_url}/version"
        version_response = self._get(version_url)
        version_response.raise_for_status()
        version_json = version_response.json()
        # Do stuff with the information.
        for version in version_json:
            if "paper" in version["loaders"]:
                return ModrinthVersion(
                    name=project_json["slug"],
                    version=version["version_number"],
                    date=datetime.strptime(version["date_published"], self._datetime_format),
                    download_url=version["files"][0]["url"]
                )
    
    def download_url(self, version: ModrinthVersion) -> str:
        return version.download_url