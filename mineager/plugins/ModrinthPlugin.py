from datetime import datetime
from .Plugin import Plugin, Version

class ModrinthVersion(Version):
    # Name would be project id
    # Version would be version id
    def __init__(self, name: str, version: str, date: datetime, download_url: str):
        super().__init__(name=name, version=version, date=date)
        self.download_url=download_url

class ModrinthPlugin(Plugin):
    _base_url = "https://api.modrinth.com/v2/project"
    _version_url = "https://api.modrinth.com/v2/version"
    type = "modrinth"

    def get_latest_version_info(self):
        # Get project information.
        project_url = f"{self._base_url}/{self.name}"
        project_response = self._get(project_url)
        project_response.raise_for_status()
        project_json = project_response.json()
        # Get version information.
        version_id = project_json["versions"][0]
        version_url = f"{self._version_url}/{version_id}"
        version_response = self._get(version_url)
        version_response.raise_for_status()
        version_json = version_response.json()
        # Define version object.
        version = ModrinthVersion(
            name = project_json["id"],
            version = version_id,
            date = version_json["date_published"],
            download_url=version_json["files"][0]["url"]
        )
        return version
    
    def download_url(self, version: ModrinthVersion) -> str:
        return version.download_url