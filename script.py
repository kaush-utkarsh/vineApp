from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FormField, validators, PasswordField
from wtforms.validators import Required,EqualTo, Optional, Length, Email
from datetime import timedelta
from functools import update_wrapper
from flask import make_response, request, current_app
from getTags import TagMedia
import json
import time
from models import *
from connectDatabase import DBConnection
import re
from vine import Vine
from config import *

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

class SignupForm(Form):
    email = TextField('Email address',  validators=[
    Required('Please provide a valid email address'),
    Length(min=6, message=(u'Email address too short')),
    Email(message=(u'That\'s not a valid email address.'))])
    password = PasswordField('Pick a secure password', validators=[
    Required(),
    Length(min=6, message=(u'Please give a longer password'))])

def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
                                # highly recommend =)
                                # https://github.com/mbr/flask-appconfig
    Bootstrap(app)

    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'
    app.config['RECAPTCHA_PUBLIC_KEY'] = \
        '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'
    app.config['CSRF_ENABLED'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Chris@cgla@localhost/cgla_studios'
    db.init_app(app)
    vine = Vine()

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            form = SignupForm(request.form)
            if form.validate():
                user = Users.query.filter_by(email = form.email.data.lower()).first()
                if user and user.check_password(form.password.data):
                    session['username'] = user.username
                    session['user_id'] = user.user_id
                    session['email'] = user.email
                    return redirect(url_for('search'))
                else:
                    return render_template('login.html', form = form, error="Invalid credentials")
            else:
                return render_template('login.html', form = form, page_title = 'Signup to Application')
        elif 'username' in session:
            return redirect(url_for('search'))
        return render_template('login.html', form = SignupForm(), page_title = 'Signup to Application')

    @app.route("/api/login", methods=["POST"])
    def login_api():
        user = Users.query.filter_by(email = request.form.get("email").lower()).first()
        if user and user.check_password(request.form.get("password").lower()):
            session['username'] = user.username
            session['user_id'] = user.user_id
            session['email'] = user.email
            return jsonify({"user_id": user.user_id, "response": 1})
        else:
            return jsonify({"response": -1})

    @app.route("/api/getvideos")
    def get_videos():
    # request.form.get("email").lower()
        all_videos = []
        if "email" in session:
            videos = SaveUserChoices.query.filter_by(email = session['email'], downloaded = 0).all()
            for video in videos:
                v = {}
                # user_details = video.user_name.split(" ")
                user_details = re.search( r'(.*)\((\d+)\)', video.user_name, re.M|re.I)
                v["video_id"] = video.id
                v["uName"] = user_details.group(1).strip() # user_details[0]
                v["uId"] = user_details.group(2).strip() # user_details[1].replace("(", "").replace(")", "")
                v["video"] = video.video_url
                v["date"] = video.created_time
                v["avatar"] = video.user_profile_picture_url
                v["prefix"] = video.prefix
                v["standard"] = video.standard
                v["text"] = video.user_text
                v["site"] = video.site
                all_videos.append(v)
        return json.dumps(all_videos)

    @app.route("/api/videodownloaded/<int:video_id>", )
    def video_downloaded(video_id):
        if "email" in session:
            video = SaveUserChoices.query.filter_by(email = session['email'], id=video_id).first()
            if video:
                video.downloaded = 1
                db.session.commit()
            return jsonify({"response": 1})
        return jsonify({"response": -1})

    @app.route('/getKeywordMedia')
    @crossdomain(origin='*')
    def getKeywordMedia():
        if "email" in session:
            keyword = request.args.get('keyword', '')
            site = request.args.get('site', '')
            if site == 'vine':
                return vine.search(keyword, media_list=[])

            session['max_tag_id'] = ''
            t = TagMedia()
            media = t.getTags(keyword)
            return media
        return jsonify({"response": -1})

    @app.route("/getplaylist", methods=['POST'])
    @crossdomain(origin='*')
    def get_playlist_videos():
        all_videos = []
        if "email" in session and request.form.get("playlist"):
            videos = db.session.query(SaveUserChoices).filter(SaveUserChoices.email == session['email'], SaveUserChoices.playlist==request.form.get("playlist"), SaveUserChoices.downloaded != -5).all()
            i = 1
            for video in videos:
                media = {}
                media["serial_no"] = i
                media["tag_url"] = video.video_url
                media["full_name"] = video.user_name
                media["profile_picture"] = video.user_profile_picture_url
                media["created_time"] = video.created_time
                media["text"] = video.user_text
                media["tag"] = video.tag
                media["id"] = video.id
                media["media_id"] = video.media_id
                media["site"] = video.site
                all_videos.append(media)
                i = i+1
        return json.dumps(all_videos)

    def get_video_playlist():
        temp_list = db.session.query(SaveUserChoices.playlist).filter(SaveUserChoices.email == session['email'], SaveUserChoices.playlist != None).distinct().all()
        playlists = []
        for pl in temp_list:
            playlists.append(pl[0])
        return playlists

    @app.route('/getplaylists')
    @crossdomain(origin='*')
    def getplaylists():
        return json.dumps(get_video_playlist())

    @app.route('/movevideos', methods=['POST'])
    @crossdomain(origin='*')
    def movevideos():
        if "email" in session:
            data = request.json
            new_playlist = data.get("playlist")
            vid_ids = data.get("vidIds", [])
            db.session.query(SaveUserChoices).filter(SaveUserChoices.email == session['email'], SaveUserChoices.downloaded == -1, SaveUserChoices.media_id.in_(vid_ids)).update({"playlist":new_playlist}, synchronize_session=False)
            db.session.commit()
            return jsonify({"response": 1})
        return jsonify({"response": -1})

    @app.route('/downloadvideos', methods=['POST'])
    @crossdomain(origin='*')
    def downloadvideos():
        if "email" in session:
            data = request.json
            playlist = data.get("playlist")
            vid_ids = data.get("vidIds", [])
            db.session.query(SaveUserChoices).filter(SaveUserChoices.email == session['email'], SaveUserChoices.playlist == playlist, SaveUserChoices.media_id.in_(vid_ids)).update({"downloaded":0}, synchronize_session=False)
            db.session.commit()
            return jsonify({"response": 1})
        return jsonify({"response": -1})

    @app.route('/getMoreVideos')
    @crossdomain(origin='*')
    def getMoreVideos():
        if "email" in session:
            keyword = request.args.get('keyword', '')
            site = request.args.get('site', '')
            if site == 'vine':
                return vine.search(keyword, session.get("nextPage", 1), media_list=[])

            t = TagMedia()
            media = t.getTags(keyword)
            return media
        return jsonify({"response": -1})

    @app.route('/saveUserChoices', methods=['POST'])
    @crossdomain(origin='*')
    def saveUserChoices():
        if "email" in session:
            i = 1
            data = request.json
            video_list = data.get("videos")
            status = data.get("status")
            playlist = data.get("playlist")

            # SaveUserChoices.query.filter_by(email = session['email'], downloaded = -1, playlist=playlist).delete()

            for k in video_list:
                user_text = k.get("text").replace("'s","")
                user_name = k.get("full_name").replace("'s","")
                saveChoices = SaveUserChoices(session['email'], k.get("tag"), k.get("tag_url"), k.get("profile_picture"), user_name, user_text, k.get("id"), status, str(k.get("prefix")+str(i)), k.get("standard"), k.get("created_time"), k.get("site"), playlist)
                db.session.add(saveChoices)
                i = i + 1
            db.session.commit()
            return jsonify({"status": 1})
        return jsonify({"response": -1})

    @app.route('/addplaylist', methods=['POST'])
    @crossdomain(origin='*')
    def addplaylist():
        if "email" in session:
            data = request.json
            playlist = data.get("playlist")

            # SaveUserChoices.query.filter_by(email = session['email'], downloaded = -1, playlist=playlist).delete()
            saveChoices = SaveUserChoices(session['email'], "playlist", "", "", "", "", 0, -5, "", "", "", "", playlist)
            db.session.add(saveChoices)
            db.session.commit()
            return jsonify({"status": 1})
        return jsonify({"response": -1})

    @app.route('/deletevideos', methods=['POST'])
    @crossdomain(origin='*')
    def deleteVideos():
        if "email" in session:
            data = request.json
            playlist = data.get("playlist")
            vid_ids = data.get("vidIds", [])
            db.session.query(SaveUserChoices).filter(SaveUserChoices.email == session['email'], SaveUserChoices.playlist == playlist, SaveUserChoices.media_id.in_(vid_ids)).delete(synchronize_session=False)
            db.session.commit()
            return jsonify({"response": 1})
        return jsonify({"response": -1})

    @app.route('/deleteplaylist', methods=['POST'])
    @crossdomain(origin='*')
    def deleteplaylist():
        if "email" in session:
            data = request.json
            playlist = data.get("playlist")
            db.session.query(SaveUserChoices).filter(SaveUserChoices.email == session['email'], SaveUserChoices.playlist == playlist).delete(synchronize_session=False)
            db.session.commit()
            return jsonify({"response": 1})
        return jsonify({"response": -1})

    @app.route('/search')
    @crossdomain(origin='*')
    def search():
        if 'username' in session:

            data = {}
            data["username"] = session['username']
            data["video_limit"] = VIDEOS_LIMIT
            data["playlists"] = get_video_playlist()
            return render_template('getKeywordTags.html', data=data)
        else:
            return redirect(url_for('login'))

    @app.route('/logout')
    def logout():
        # remove the username from the session if it's there
        session.pop('username', None)
        return redirect(url_for('login'))
    return app

if __name__ == '__main__':
    create_app().run(debug=True,host='0.0.0.0')
