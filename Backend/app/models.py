from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """
    Modelo do banco de dados para um Usuário.
    """
    id = db.Column(db.Integer, primary_key=True)
    primeiro_nome = db.Column(db.String(64), index=True, nullable=False)
    sobrenome = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    senha_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'