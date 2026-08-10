"""Restore versioned runtime artifacts for hosted dashboard deployments."""

from __future__ import annotations

import hashlib
import os
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from src.config import METRICS_PATH, MODEL_PATH, ROOT

DEPLOYMENT_ARTIFACT_URL = os.getenv(
    "FLIGHTPULSE_ARTIFACT_URL",
    "https://github.com/abhiiii2007/flight-delay-platform/releases/download/"
    "deployment-v1/flightpulse-deployment-artifacts.tar.gz",
)
DEPLOYMENT_ARTIFACT_SHA256 = os.getenv(
    "FLIGHTPULSE_ARTIFACT_SHA256",
    "6fd2678c55c1d1ae0d56dc2a3a9acf5e7cf77107977404fd8e0f474c03665b1b",
)
DATABASE_PATH = ROOT / "data/flights.db"
EXPECTED_MEMBERS = {
    "flights.db": DATABASE_PATH,
    "processed/delay_model.joblib": MODEL_PATH,
    "processed/delay_model.metrics.json": METRICS_PATH,
}


def runtime_artifacts_exist() -> bool:
    return all(path.exists() for path in EXPECTED_MEMBERS.values())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _extract_expected_members(archive_path: Path) -> None:
    with tarfile.open(archive_path, "r:gz") as archive:
        members = {member.name: member for member in archive.getmembers() if member.isfile()}
        if set(members) != set(EXPECTED_MEMBERS):
            raise ValueError("Deployment bundle does not contain the expected runtime artifacts")
        for name, destination in EXPECTED_MEMBERS.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(members[name])
            if source is None:
                raise ValueError(f"Unable to read deployment artifact: {name}")
            with source, destination.open("wb") as target:
                while chunk := source.read(1024 * 1024):
                    target.write(chunk)


def ensure_runtime_artifacts() -> bool:
    """Download verified hosted artifacts when the normal local files are absent."""
    if runtime_artifacts_exist():
        return False
    if not DEPLOYMENT_ARTIFACT_URL or not DEPLOYMENT_ARTIFACT_SHA256:
        raise FileNotFoundError("Runtime artifacts are missing and deployment download is disabled")
    if urlparse(DEPLOYMENT_ARTIFACT_URL).scheme != "https":
        raise ValueError("Deployment artifact URL must use HTTPS")

    with tempfile.TemporaryDirectory(prefix="flightpulse-") as temporary_directory:
        archive_path = Path(temporary_directory) / "deployment-artifacts.tar.gz"
        urllib.request.urlretrieve(DEPLOYMENT_ARTIFACT_URL, archive_path)  # nosec B310
        actual_sha256 = _sha256(archive_path)
        if actual_sha256 != DEPLOYMENT_ARTIFACT_SHA256:
            raise ValueError("Deployment artifact checksum verification failed")
        _extract_expected_members(archive_path)

    if not runtime_artifacts_exist():
        raise FileNotFoundError("Deployment artifacts were not restored successfully")
    return True
