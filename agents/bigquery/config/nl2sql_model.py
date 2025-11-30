import os
from dataclasses import dataclass


@dataclass
class Nl2SqlModelConfig:
    google_cloud_project: str
    google_cloud_location: str
    nl2sql_model: str

    @classmethod
    def from_env(cls) -> "Nl2SqlModelConfig":
        """Create configuration from environment variables.

        Returns:
            Nl2SqlModelConfig: Configuration instance populated from environment variables.

        Raises:
            KeyError: If required environment variables are not set.
        """
        return cls(
            google_cloud_project=os.environ["GOOGLE_CLOUD_PROJECT"],
            google_cloud_location=os.environ["GOOGLE_CLOUD_LOCATION"],
            nl2sql_model=os.environ["NL2SQL_MODEL"],
        )
