import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from .activity import prepare_fields


def now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.lock = threading.RLock()
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, updated TEXT NOT NULL, document TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS knowledge (id TEXT PRIMARY KEY, title TEXT NOT NULL, source TEXT NOT NULL, text TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS plans (id TEXT PRIMARY KEY, updated TEXT NOT NULL, document TEXT NOT NULL)')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(str(self.path), timeout=10)
        try:
            with db:
                yield db
        finally:
            db.close()

    def create(self, fields):
        fields = prepare_fields(fields)
        doc = dict(id=uuid.uuid4().hex, created_at=now(), updated_at=now(), revision=0,
                   title=fields.get('title', '未命名演练'), story=fields.get('story', ''),
                   constraints=fields.get('constraints', ''), participants=fields.get('participants', '3'),
                   remaining=fields.get('remaining', '3'), mode=fields.get('mode', 'demo'),
                   summary=None, events=[], selected_event=None, hints=[], logs=[], observation='')
        doc['activity_config'] = fields.get('activity_config')
        doc['presentation'] = None
        doc['presentation_history'] = []
        self.save(doc)
        return doc

    def get(self, session_id):
        with self.connect() as db:
            row = db.execute('SELECT document FROM sessions WHERE id=?', (session_id,)).fetchone()
        if not row:
            raise KeyError('演练不存在。')
        return json.loads(row[0])

    def save(self, doc):
        doc['updated_at'] = now()
        with self.lock, self.connect() as db:
            db.execute('INSERT OR REPLACE INTO sessions VALUES (?, ?, ?)', (doc['id'], doc['updated_at'], json.dumps(doc, ensure_ascii=False)))

    def listing(self):
        with self.connect() as db:
            rows = db.execute('SELECT document FROM sessions ORDER BY updated DESC LIMIT 100').fetchall()
        result = []
        for row in rows:
            d = json.loads(row[0])
            result.append({k: d[k] for k in ('id', 'title', 'updated_at', 'mode') } | {'event_count': len(d['events']), 'hint_count': len(d['hints'])})
        return result

    def documents(self):
        with self.connect() as db:
            return [dict(zip(('id', 'title', 'source', 'text'), r)) for r in db.execute('SELECT * FROM knowledge ORDER BY rowid')]

    def plans(self):
        with self.connect() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT document FROM plans ORDER BY updated DESC LIMIT 100')]

    def add_plan(self, fields):
        fields = prepare_fields(fields)
        if not fields['story'].strip():
            from .model import AgentError
            raise AgentError('先选择一个活动起点或填写情境，再保存方案。')
        fields.pop('mode', None)
        doc = dict(id=uuid.uuid4().hex, updated_at=now(), fields=fields)
        with self.connect() as db:
            db.execute('INSERT INTO plans VALUES (?, ?, ?)', (doc['id'], doc['updated_at'], json.dumps(doc, ensure_ascii=False)))
        return doc

    def add_document(self, title, source, text):
        doc = dict(id=uuid.uuid4().hex, title=title, source=source, text=text)
        with self.connect() as db:
            db.execute('INSERT INTO knowledge VALUES (?, ?, ?, ?)', tuple(doc.values()))
        return doc

