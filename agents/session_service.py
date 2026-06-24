"""JSON-file-backed session service. Survives restarts."""

import json
from pathlib import Path

from google.adk.sessions import InMemorySessionService, Session


class FileSessionService(InMemorySessionService):
    """Persists sessions to a JSON file. Restores on restart."""

    def __init__(self, path: str = "sessions.json"):
        super().__init__()
        self._path = Path(path)
        if self._path.exists() and self._path.stat().st_size:
            self._load()

    def _load(self):
        raw = json.loads(self._path.read_text())
        for app_name, users in raw.get("sessions", {}).items():
            self.sessions.setdefault(app_name, {})
            for user_id, sessions in users.items():
                self.sessions[app_name].setdefault(user_id, {})
                for sid, data in sessions.items():
                    self.sessions[app_name][user_id][sid] = Session.model_validate(data)
            self.user_state.update(raw.get("user_state", {}))
            self.app_state.update(raw.get("app_state", {}))

    def _save(self):
        raw = {"sessions": {}, "user_state": self.user_state, "app_state": self.app_state}
        for app_name, users in self.sessions.items():
            raw["sessions"].setdefault(app_name, {})
            for user_id, sessions in users.items():
                raw["sessions"][app_name].setdefault(user_id, {})
                for sid, session in sessions.items():
                    raw["sessions"][app_name][user_id][sid] = session.model_dump()
        self._path.write_text(json.dumps(raw, indent=2, default=str))

    async def create_session(self, **kwargs):
        session = await super().create_session(**kwargs)
        self._save()
        return session

    async def append_event(self, session, event):
        result = await super().append_event(session, event)
        self._save()
        return result

    async def delete_session(self, **kwargs):
        await super().delete_session(**kwargs)
        self._save()

    def create_session_sync(self, **kwargs):
        session = super().create_session_sync(**kwargs)
        self._save()
        return session
