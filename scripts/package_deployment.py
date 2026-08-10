"""Build a deterministic hosted-dashboard artifact bundle."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist/flightpulse-deployment-artifacts.tar.gz"
ARTIFACTS = {
    "flights.db": ROOT / "data/flights.db",
    "processed/delay_model.joblib": ROOT / "data/processed/delay_model.joblib",
    "processed/delay_model.metrics.json": ROOT / "data/processed/delay_model.metrics.json",
}


def package(output: Path = DEFAULT_OUTPUT) -> str:
    missing = [str(path) for path in ARTIFACTS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing deployment artifacts: {', '.join(missing)}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for name, path in ARTIFACTS.items():
                    member = tarfile.TarInfo(name)
                    member.size = path.stat().st_size
                    member.mode = 0o644
                    member.mtime = 0
                    with path.open("rb") as source:
                        archive.addfile(member, source)

    digest = hashlib.sha256()
    with output.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checksum = package(args.output)
    print(f"Created {args.output}")
    print(f"SHA-256: {checksum}")


if __name__ == "__main__":
    main()
