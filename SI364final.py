# SI364 Final Project - Baseball Application
# by Cameron Chandra 


#############################
# Setup and App configuration 
#############################
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,BooleanField, IntegerField, ValidationError,PasswordField, SelectMultipleField
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell 
from flask_migrate import Migrate, MigrateCommand
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from requests_oauthlib import OAuth2Session 
from requests.exceptions import HTTPError
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import datetime
import tweepy
import json
from ohmysportsfeedspy import MySportsFeeds



os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' 
basedir = os.path.abspath(os.path.dirname(__file__))

#### OAuth configurations #### Code pulled from Sample-Login-OAuth-Example Discussion code
class Auth:
    CLIENT_ID = ('98805661756-p7gv7a15o51h81crbqr91mgi8qibmmk9.apps.googleusercontent.com') 
    CLIENT_SECRET = 'rlNTv55JVwwn7Zc6h3cyF0NV'
    REDIRECT_URI = 'http://localhost:5000/gCallback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']


class Config:
    APP_NAME = "Test Google Login"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "something secret"


class DevConfig(Config):
    DEBUG = True
    USE_RELOADER = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:29Malysana@localhost:5432/SI364finalprojectcamchan"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


class ProdConfig(Config):
    DEBUG = False
    USE_RELOADER = True
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/364finaldb" 
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}
#### App configuration ####
app = Flask(__name__)
app.config.from_object(config['dev']) 
db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"
# shell definition
def make_shell_context():
    return dict( app=app, db=db, Song=Song, Artist=Artist, Album=Album)
# manager function
manager.add_command("shell", Shell(make_context=make_shell_context))



#############################
#### Model Definitions #### 
#############################

user_team = db.Table('user_team',db.Column('player_id', db.Integer, db.ForeignKey('players.id')),db.Column('team_id',db.Integer, db.ForeignKey('teams.id')))

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    teams = db.relationship('Team',backref='User')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Team(db.Model):
	__tablename__ = 'teams'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(100))
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
	players = db.relationship('Player',secondary=user_team,backref=db.backref('teams',lazy='dynamic'),lazy='dynamic')

class Player(db.Model):
	__tablename__ = 'players'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(100))
	mlb_team = db.Column(db.String(100))
	position = db.Column(db.String(100)) 
	avg = db.Column(db.Float)
	hr = db.Column(db.Integer)
	steals = db.Column(db.Integer)
	runs = db.Column(db.Integer)

class Tweet(db.Model):
	__tablename__ = 'tweets'
	id = db.Column(db.Integer,primary_key=True)
	tweet = db.Column(db.String(1000))
	player_name = db.Column(db.String(100))


# Code pulled from Sample-Login-OAuth-Example Discussion code
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


""" OAuth Session creation """
def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth


#############################
 #### Helper Functions #### 
#############################

# Non-get or create helper function
def get_player_info(player_name):
	player_name = player_name.lower()
	player_name = player_name.replace(' ','-')
	msf = MySportsFeeds(version="1.2")
	msf.authenticate("cameronchandra", "29Malysana")
	output = msf.msf_get_data(league='mlb',season='latest',format='json',feed='cumulative_player_stats',player=player_name)
	mlb_team = output['cumulativeplayerstats']['playerstatsentry'][0]['team']['Abbreviation']
	position = output['cumulativeplayerstats']['playerstatsentry'][0]['player']['Position']
	avg = output['cumulativeplayerstats']['playerstatsentry'][0]['stats']['BattingAvg']['#text']
	hr = output['cumulativeplayerstats']['playerstatsentry'][0]['stats']['Homeruns']['#text']
	steals = output['cumulativeplayerstats']['playerstatsentry'][0]['stats']['StolenBases']['#text']
	runs = output['cumulativeplayerstats']['playerstatsentry'][0]['stats']['Runs']['#text']
	return mlb_team,position,avg,hr,steals,runs


def get_player_by_id(id):
	p = Player.query.filter_by(id=id).first()
	return p

def get_or_create_team(name,current_user,player_list=[]):
	team = Team.query.filter_by(name=name,user_id=current_user.id).first()
	if team:
		return team
	else:
		team = Team(name=name,user_id= current_user.id,players=[])
		for player in player_list:
			team.players.append(player)
		db.session.add(team)
		db.session.commit()
	return team

def get_or_create_tweet(name):
	tweet = Tweet.query.filter_by(player_name=name).first()
	if tweet:
		return tweet
	else:
		twitter_info = get_tweets(name)
		for tw in twitter_info:
			tweet = tw['text']
			tweet = tweet.strip()
			tweet = Tweet(tweet=tweet,player_name=name)
			db.session.add(tweet)
			db.session.commit()
	return tweet


def get_or_create_player(name):
	player = Player.query.filter_by(name=name).first()
	if player:
		return player
	else:
		player_stats = get_player_info(name)
		mlb_team = player_stats[0]
		position = player_stats[1]
		avg = player_stats[2]
		hr = player_stats[3]
		steals = player_stats[4]
		runs = player_stats[5]
		player = Player(name=name,mlb_team=mlb_team,position=position,avg=avg,hr=hr,steals=steals,runs=runs)
		db.session.add(player)
		db.session.commit()
	return player

# Non-get or create helper function
def get_tweets(player_name): 
	consumer_key = '5vITiWP75mYmKq9Fiu7xeGIzV'
	consumer_secret = 'rF6ux0UbNnoORylmEMqvJolZuQkcyuIkiD4kBap23W0TTLgeqE'
	access_token = '612102861-6uoS0nS9MzACUZtACCntXdiHJxeHQG7Ls69OuCM7'
	access_token_secret = '5BKXmJR9eV5SxLRScfMT9ht0hhDEWHrq2IDZzSfDADHAs'
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth, parser=tweepy.parsers.JSONParser()) 
	player_name = player_name.replace(' ','')
	hashtag = '#'+player_name
	results = api.search(q=hashtag,count=3)
	return results['statuses']

#############################
	#### Error Handlers #### 
#############################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


#############################
	#### Forms #### 
#############################

# code pulled from my Homework 4 file - Registration and Login class definitions
class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class TeamForm(FlaskForm):
	team_name = StringField("What is the name of your team?",validators=[Required()])
	player_picks = SelectMultipleField('Choose your players')
	submit = SubmitField('Create Team')
	# Custom validation
	def validate_team(self,field):
		for team in field.data:
			t = Team.query.filter_by(name=team).first()
			if t:
				raise ValidationError('This team has already been created, try a different name.')

class TweetForm(FlaskForm):
	players = StringField("Enter saved player names to see tweets about them (seperate with commas): ",validators=[Required()])
	submit = SubmitField()
	# Custom validation
	def validate_players(self,field):
		for player in field.data.split(','):
			p = Player.query.filter_by(name=player.strip()).first()
			if not p:
				raise ValidationError('This player(s) has not been saved. Go to the Home Page and enter the player names.')

class RosterForm(FlaskForm):
	first = StringField("Enter a first basemen", validators=[])
	second = StringField("Enter a second basemen", validators=[])
	short = StringField("Enter a shortstop", validators=[])
	third = StringField("Enter a third basemen", validators=[])
	catcher = StringField("Enter a catcher", validators=[])
	left = StringField("Enter a left fielder", validators=[])
	right = StringField("Enter a right fielder", validators=[])
	center = StringField("Enter a center fielder", validators=[])
	submit = SubmitField('Add Players')

class UpdateTeamNameForm(FlaskForm):
	name = StringField("Update the name of your team",validators=[Required()])
	submit = SubmitField("Update")

class DeleteButtonForm(FlaskForm):
	submit = SubmitField('Delete')
#############################
	#### Routes #### 
#############################

@app.route('/',methods=['GET','POST'])
def index(): 
	form = RosterForm()
	if form.validate_on_submit():
		get_or_create_player(form.first.data)
		get_or_create_player(form.second.data)
		get_or_create_player(form.short.data)
		get_or_create_player(form.third.data)
		get_or_create_player(form.catcher.data)
		get_or_create_player(form.left.data)
		get_or_create_player(form.right.data)
		get_or_create_player(form.center.data)
		flash('Players added!')
		return redirect(url_for('create_team'))
	return render_template('index.html',form=form,current_user=current_user)

# code pulled from my Homework 4 file
@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)


@app.route('/create_team',methods=['GET','POST'])
@login_required
def create_team():
	form = TeamForm() 
	players = Player.query.all()
	choices = [(p.id,p.name) for p in players]
	form.player_picks.choices = choices
	if request.method == 'POST':
		player_list = form.player_picks.data
		items = [get_player_by_id(int(id)) for id in player_list]
		team = get_or_create_team(form.team_name.data,current_user=current_user,player_list=items)
		flash('Successfully created team!')
		return redirect(url_for('show_teams',team=team))
	return render_template('team.html',form=form)

@app.route('/show_teams')
@login_required
def show_teams():
	form = DeleteButtonForm()
	team = Team.query.filter_by(user_id=current_user.id).all()
	return render_template('roster.html',team=team,form=form)


@app.route('/delete/<team>',methods=["GET","POST"])
def delete(team):
	db.session.delete(Team.query.filter_by(name=team).first())
	flash("Deleted team {}".format(team))
	return redirect(url_for('show_teams'))


@app.route('/team/<id_num>',methods=['GET','POST'])
def single_team(id_num):
	form = UpdateTeamNameForm()
	id_num = int(id_num)
	team = Team.query.filter_by(id=id_num).first()
	players = team.players.all()
	return render_template('single_team.html',team=team,players=players,form=form)


@app.route('/update/<name>',methods=['GET','POST'])
def update(name):
	form = UpdateTeamNameForm()
	if form.validate_on_submit():
		items = Team.query.filter_by(name=name).first()
		items.name = form.name.data
		db.session.commit()
		flash('Updated team name')
		return redirect(url_for('show_teams'))
	return render_template('update_name.html',items=items,form=form)

@app.route('/show_stats')
def show_stats(): 
	team = Team.query.filter_by(user_id=current_user.id).all()
	return render_template('stat_roster.html',team=team) 

@app.route('/team_stat/<id_num>')
def single_stat_team(id_num):
	id_num = int(id_num)
	team = Team.query.filter_by(id=id_num).first()
	players = team.players.all()
	return render_template('single_team_stats.html',team=team,players=players)


@app.route('/show_news',methods=['GET','POST'])
def show_news():
	form = TweetForm()
	player_dict = {}
	if form.validate_on_submit():
		player_name = form.players.data
		player_lst = player_name.split(',')
		for player in player_lst:
			get_or_create_tweet(player.strip())
			tweet = db.session.query(Tweet.tweet).filter_by(player_name=player.strip()).all()
			player_dict[player] = tweet
	return render_template('player_news.html',form=form,player_dict=player_dict)



#### Login and Logout routes #### Code pulled from Sample-Login-OAuth-Example Discussion code
@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    form = LoginForm()
    if form.validate_on_submit():
    	user = User.query.filter_by(email=form.email.data).first()
    	if user is not None and user.verify_password(form.password.data):
    		login_user(user, form.remember_me.data)
    		return redirect(request.args.get('next') or url_for('index'))
    	flash('Invalid username or password.')
    return render_template('login.html', auth_url=auth_url,form=form)


@app.route('/gCallback')
def callback():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args: 
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
            user.name = user_data['name']
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))














if __name__ == "__main__":
    db.create_all()
    manager.run()

