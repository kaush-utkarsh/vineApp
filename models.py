from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "Users"
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(254), unique=True)
    firstname = db.Column(db.String(254))
    lastname = db.Column(db.String(254))
    email = db.Column(db.String(254))
    password = db.Column(db.String(254))
    active = db.Column(db.String(254))
    time_registered = db.Column(db.DateTime)

    def __init__(self, username, password, firstname, lastname, email, active, time_registered):
        self.username = username.lower()
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.email = email.lower()
        self.active = active
        self.time_registered = time_registered

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return self.password ==  password


class SaveUserChoices(db.Model):
    __tablename__ = "saveUserChoices"
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.Integer)
    tag = db.Column(db.String(254))
    video_url = db.Column(db.String(254))
    user_profile_picture_url = db.Column(db.String(254))
    user_name = db.Column(db.String(254))
    user_text = db.Column(db.String(254))
    media_id = db.Column(db.String(254))
    downloaded = db.Column(db.Integer)
    prefix = db.Column(db.String(254))
    standard = db.Column(db.Float)
    created_time = db.Column(db.DateTime)

    def __init__(self, email, tag, video_url, user_profile_picture_url, user_name, user_text, media_id, downloaded, prefix, standard, created_time):
        self.email = email.lower()
        self.tag = tag
        self.video_url = video_url
        self.user_profile_picture_url = user_profile_picture_url
        self.user_name = user_name
        self.user_text = user_text
        self.media_id = media_id
        self.downloaded = downloaded
        self.prefix = prefix
        self.standard = standard
        self.created_time = created_time