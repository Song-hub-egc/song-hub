import threading
import time
from copy import deepcopy
from typing import Dict, List, Optional, Tuple


class FakeNodoService:
    """In-memory simulation of the minimum Zenodo API surface used in development."""

    def __init__(self):
        self._lock = threading.Lock()
        self._depositions: Dict[int, Dict] = {}
        self._next_id = 1

    @staticmethod
    def _now() -> int:
        return int(time.time())

    @staticmethod
    def _make_doi(deposition_id: int, version: int) -> str:
        return f"10.12345/fakenodo.{deposition_id}.v{version}"

    def _conceptrecid(self, deposition_id: int) -> int:
        return 100 + deposition_id

    def status(self) -> Dict[str, int]:
        with self._lock:
            return {"depositions_count": len(self._depositions), "next_id": self._next_id}

    def create_deposition(self, metadata: Dict) -> Dict:
        with self._lock:
            dep_id = self._next_id
            self._next_id += 1

            now = self._now()
            self._depositions[dep_id] = {
                "id": dep_id,
                "metadata": metadata,
                "files": [],
                "created": now,
                "last_modified": now,
                "published_versions": [],
                "conceptrecid": self._conceptrecid(dep_id),
            }

            response = deepcopy(self._depositions[dep_id])
            response["links"] = {"files": f"/fakenodo/api/deposit/depositions/{dep_id}/files"}
            return response

    def list_depositions(self) -> List[Dict]:
        with self._lock:
            return [{"id": d["id"], "metadata": deepcopy(d["metadata"])} for d in self._depositions.values()]

    def get_deposition(self, deposition_id: int) -> Optional[Dict]:
        with self._lock:
            dep = self._depositions.get(deposition_id)
            if not dep:
                return None

            payload = deepcopy(dep)
            payload["links"] = {"files": f"/fakenodo/api/deposit/depositions/{dep['id']}/files"}

            if dep["published_versions"]:
                latest = dep["published_versions"][-1]
                payload["doi"] = latest["doi"]
                payload["version"] = latest["version"]
            else:
                payload["doi"] = self._make_doi(dep["id"], 1)
                payload["version"] = 1

            return payload

    def update_metadata(self, deposition_id: int, metadata: Dict) -> Optional[Dict]:
        with self._lock:
            dep = self._depositions.get(deposition_id)
            if not dep:
                return None
            dep["metadata"] = metadata
            dep["last_modified"] = self._now()
            return {"id": deposition_id, "metadata": deepcopy(metadata)}

    def delete_deposition(self, deposition_id: int) -> bool:
        with self._lock:
            return self._depositions.pop(deposition_id, None) is not None

    def add_file(self, deposition_id: int, filename: str) -> Optional[Dict]:
        with self._lock:
            dep = self._depositions.get(deposition_id)
            if not dep:
                return None
            dep["files"].append(filename)
            dep["last_modified"] = self._now()
            latest_version = dep["published_versions"][-1]["version"] if dep["published_versions"] else 1
            return {
                "filename": filename,
                "id": filename,
                "conceptrecid": self._conceptrecid(deposition_id),
                "doi": self._make_doi(deposition_id, latest_version),
            }

    def publish(self, deposition_id: int) -> Optional[Tuple[Dict, bool]]:
        with self._lock:
            dep = self._depositions.get(deposition_id)
            if not dep:
                return None

            current_files = list(dep["files"])
            last_pub = dep["published_versions"][-1] if dep["published_versions"] else None
            create_new_version = not last_pub or last_pub["files"] != current_files

            if create_new_version:
                version = (last_pub["version"] + 1) if last_pub else 1
                doi = self._make_doi(deposition_id, version)
                record = {
                    "version": version,
                    "files": current_files,
                    "published_at": self._now(),
                    "conceptrecid": self._conceptrecid(deposition_id),
                    "doi": doi,
                }
                dep["published_versions"].append(record)
                dep["last_modified"] = self._now()
                return record, True

            if last_pub:
                return deepcopy(last_pub), False

            fallback = {
                "version": 1,
                "files": current_files,
                "published_at": dep["created"],
                "conceptrecid": self._conceptrecid(deposition_id),
                "doi": self._make_doi(deposition_id, 1),
            }
            return fallback, False

    def list_versions(self, deposition_id: int) -> Optional[List[Dict]]:
        with self._lock:
            dep = self._depositions.get(deposition_id)
            if not dep:
                return None
            return [deepcopy(v) for v in dep["published_versions"]]

    def reset(self):
        """Utility method used in tests to clear all in-memory state."""
        with self._lock:
            self._depositions.clear()
            self._next_id = 1


fakenodo_service = FakeNodoService()
