from flask import Flask, render_template, request, redirect
import json, requests, sys, smtplib, pdb
from flask_wtf import Form
from flask_mail import Mail, Message
from wtforms import StringField, TextAreaField, SubmitField, validators
app = Flask(__name__)
import jinja2
env = jinja2.Environment()
env.globals.update(zip=zip)
app.config['MAIL_SERVER'] = 'smtp.aynst.in'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '--EMAIL--'
app.config['MAIL_PASSWORD'] = '**PASSWORD**'

class ContactForm(Form):
	email = StringField('Your e-mail address:')
	submit = SubmitField('SUBSCRIBE')

mail = Mail(app)

@app.route('/')
def home():
	return render_template('index.html')


@app.route('/place' ,methods = ['POST', 'GET'])
def locate():
	city = request.form['place']
	typeof = request.form.get('menu')
	location = city
	url = 'http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=--APIKEY--&units=metric' % (location)
	weatherResponse = requests.get(url)
	weatherResponse.raise_for_status()
	city = city.title()
	#Load JSON Data into a python variable
	weatherData = json.loads(weatherResponse.text)

	#Weather descrptions
	w = weatherData
	country = w['sys']['country']
	curr = w['weather'][0]['description']
	curr = curr.title()
	icon = w['weather'][0]['icon']
	tempNow = w['main']['temp']
	tempNow = str(tempNow)[:2]
	windSpeed = w['wind']['speed']
	humidity = w['main']['humidity']
	temp_min = w['main']['temp_min']
	temp_max = w['main']['temp_max']
	#iconLink =  'giphy.gif'
	if icon == '01d':
		iconLink = 'sunny.png'
	elif icon == '02d':
		iconLink = 'sunshine.png'
	elif icon == '03d':
		iconLink = 'cloudy.png'
	elif icon == '04d':
		iconLink = 'cloud1.png'
	elif icon == '10d':
		iconLink = 'rainy.png'
	elif icon == '10n':
		iconLink = 'rainy.png'
	elif icon == '01n':
		iconLink = 'foggy.png'
	elif icon == '03n':
		iconLink = 'night cloud.png'
	elif icon == '02n':
		iconLink = 'clouds.png'
	elif icon == '04n':
		iconLink = 'few clouds.png'
	elif icon == '50n':
		iconLink = 'haze.png'
	else:
		iconLink = 'giphy.gif'

	#Get places

	url = 'https://maps.googleapis.com/maps/api/geocode/json?address='+location+'&key=--APIKEY--'
	gpsResponse = requests.get(url)
	gpsResponse.raise_for_status()
	gps = json.loads(gpsResponse.text)
	fullName = gps['results'][0]['formatted_address']
	lat = gps['results'][0]['geometry']['location']['lat']
	lng = gps['results'][0]['geometry']['location']['lng']
	fullName = fullName.title()

	#Get location data from Google Places API

	url='https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(lat)+','+str(lng)+'&type='+ str(typeof) +'&rankby=distance&key=--APIKEY--'
	placesResponse = requests.get(url)
	placesResponse.raise_for_status()
	places = json.loads(placesResponse.text)
	p = places
	nameList = []		  #stores names
	ratingList = []		#stores ratings
	photosList = []		#stores photo reference
	placeURLList = []	  #stores photos
	addressList = []

	#Get place name
	for i in range(0,19):
		if 'photos' in p['results'][i]:
			pref = p['results'][i]['photos'][0]['photo_reference']
			photosList.insert(i, p['results'][i]['photos'])
			placeURLList.insert(i,'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference='+pref+'&key=--APIKEY--')
		else:
			placeURLList.insert(i,'http://placehold.it/158x158')
		if 'name' in p['results'][i]:
			nameList.insert(i,p['results'][i]['name'])
			if 'rating' in places['results'][i]:
				ratingList.insert(i,p['results'][i]['rating'])
			else:
				ratingList.insert(i,'NA')
			if 'vicinity' in p['results'][i]:
				addressList.insert(i, p['results'][i]['vicinity'])


	#iconLink = 'http://openweathermap.org/img/w/'+icon+'.png'
	return render_template('index.html', lat=lat, lng=lng, fullName=fullName, city=city, curr=curr, icon=icon, tempNow=tempNow, windSpeed=windSpeed, iconLink=iconLink, humidity=humidity, tempList = zip(nameList, ratingList, placeURLList, addressList), typeof = typeof, temp_min = temp_min, temp_max = temp_max)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/confirmation')
def sub():
	return render_template('success.html')

@app.route('/privacy')
def privacy():
	return render_template('privacy.html')

@app.route('/conditions')
def conditions():
	return render_template('conditions.html')

@app.route('/play')
def playground():
	return render_template('play.html')

@app.route('/sitemap')
def sitemap():
	return render_template('sitemap.xml')

@app.route('/construct', methods = ['POST', 'GET'])
def construction():
	form = ContactForm()
	if request.method == 'POST':
			msg = Message("Message from your visitor",
						  sender='--EMAIL--',
						  recipients=['--RECIPIENTS EMAIL--'])
			msg.body = """
			From: <%s>
			""" % (form.email.data)
			mail.send(msg)
			return redirect('confirmation')

	elif request.method == 'GET':
		return render_template('construct.html', form=form)

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def notFound(e):
	return render_template('404.html'), 404

@app.errorhandler(400)
def forbidden(e):
	return render_template('400.html'), 403

if __name__ == '__main__':
	app.run(threaded=True)
