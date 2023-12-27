import json
from database.database import db


class APICall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    machine = db.Column(db.String(128))
    username = db.Column(db.String(128))
    client_ip = db.Column(db.String(128))
    endpoint = db.Column(db.String(128))
    status_code = db.Column(db.Integer)
    parameters = db.Column(db.Text)  # Storing parameters as JSON string
    response_time = db.Column(db.Float)
    method = db.Column(db.String(10))
    response_body = db.Column(db.Text)  # Optional, can be large
    error_message = db.Column(db.String(512))
    user_agent = db.Column(db.String(256))
    referrer = db.Column(db.String(256))

    def __repr__(self):
        return f"<APICall {self.username} from {self.machine}>"

    def set_parameters(self, params):
        self.parameters = json.dumps(params) if params else None

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
