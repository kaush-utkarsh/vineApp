
from flask import Flask, render_template, request, session
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
	email = TextField('Email address',	validators=[
        	Required('Please provide a valid email address'),
        	Length(min=6, message=(u'Email address too short')),
        	Email(message=(u'That\'s not a valid email address.'))])
	password = PasswordField('Pick a secure password', validators=[
        	Required(),
        	Length(min=6, message=(u'Please give a longer password'))])
	agree = BooleanField('I agree all your Terms of Services',
        	validators=[Required(u'You must accept our Terms of Service')])


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

	@app.route('/signup', methods=['GET', 'POST'])
	def signup():
		if request.method == 'POST':
	        	form = SignupForm(request.form)
        		if form.validate():
				if form.email.data != 'dev@algoscale.com':
					form.email.errors.append('Please enter correct Email')
					return render_template('signinpage.html',  signinpage_form = form)
				if form.password.data != 'password':
                			form.password.errors.append('Please enter correct Password')
                			return render_template('signinpage.html',  signinpage_form = form)
				session['username']=form.email.data
				print form.email.data 
            			#return render_template('home.html', email=form.email.data)
            			return render_template('getKeywordTags.html')
			else:
				 return render_template('signup.html', form = form, page_title = 'Signup to Application')
		return render_template('signup.html', form = SignupForm(), page_title = 'Signup to Application')

	@app.route('/getKeywordMedia')
	@crossdomain(origin='*')
	def getKeywordMedia():
		keyword = request.args.get('keyword', '')
		t = TagMedia()
		media = t.getTags(keyword)
		list = []
                for rm in media:
			print rm
			tag_info = {}
                        tag_info["tag_url"] = rm.get_standard_resolution_url()
			tag_info["full_name"] = rm.user.full_name
			tag_info["profile_picture"] = rm.user.profile_picture
			tag_info["created_time"] = str(rm.created_time) 
			print rm.created_time
			#tag_info["type"] = rm.type
			list.append(tag_info)
    		return json.dumps(list)
	
	return app

if __name__ == '__main__':
	create_app().run(debug=True,host='0.0.0.0')
