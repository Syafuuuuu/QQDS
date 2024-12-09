from flask import Flask, render_template , request, redirect, url_for, flash, redirect
from urllib.parse import urljoin
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import plotly.graph_objects as go

import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.io as pio
pio.templates
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
import seaborn as sns
import mysql.connector
import csv

from flask_mysqldb import MySQL

app = Flask (__name__)

app.config ['MYSQL_HOST'] = 'localhost'
app.config ['MYSQL_USER'] = 'root'
app.config ['MYSQL_PASSWORD'] = ''
app.config ['MYSQL_DB'] = 'qqdb'

mysql = MySQL(app)

class UploadFileForm(FlaskForm):
	file = FileField("File")
	submit = SubmitField("Upload File")

app.config['SECRET_KEY'] = 'creme'

@app.route('/')
def start():
	return redirect(url_for('loginPage'))

@app.route('/loginPage')
def loginPage():

		return render_template('loginPage.html')

@app.route('/login', methods=['POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		if username == 'QuoffeAdmin' and password == 'QuoffeCommunity':
			return redirect(url_for('home'))
		else:
			return '<script>alert("Incorrect username or password."); window.location="/loginPage";</script>'

@app.route('/home', methods=['POST','GET'])
def home():

	form = UploadFileForm()
	if form.validate_on_submit():

		try:
			file = form.file.data

			# Perform data cleaning using pandas or other libraries
			df = pd.read_csv(file)
			df.drop(["Timestamp", "Email address"], inplace=True, axis=1)

			df.rename(columns={"Gender": "gender", "Age": "age", "Occupations": "occ", "Staying at": "stay", "Frequent places visited in UUM": "fplace", "Which DKG do you most frequently visits?": "fhall", "Have you heard of Quoffe Coffee before?": "heard", "Where did you hear us from?": "heardFrom", "Customers’ Favorite Product": "favProd", "Preferred places for consumption of the product": "consumption", "Loyalty to the brand": "loyalty", "Likelihood of Customer to Recommend Quoffe Coffee to Friends or Colleagues": "Q1", "Overalls Customer Satisfaction or Dissatisfaction Level": "Q2", "Customers’ Review on Price of Beverages": "Q3", "Customers’ Rate to The Quoffe Product Quality": "Q4", "Customers’ Perception of Quoffe Customer Service": "Q5", "Changes of Customer Perception": "Q6", "The Frequency of Quoffe Promotion": "Q7", "The Frequency of Customers Purchase": "Q8"}, inplace=True)

			#--------Number Variables-----------
			recordCount = df.shape[0]
			female = df[df['gender'] == 'Female'].shape[0]/recordCount*100
			knows = df[df['heard'] == 'Yes'].shape[0]/recordCount*100
			ori0 = df[df['favProd'] == 'Ori Coffee'].shape[0]
			coco0 = df[df['favProd'] == 'Merry Coco'].shape[0]
			my0 = df[df['favProd'] == 'Malaysiano'].shape[0]
			hork0 = df[df['favProd'] == 'Horkasai'].shape[0]
			ori = df[df['favProd'] == 'Ori Coffee'].shape[0]/recordCount*100
			coco = df[df['favProd'] == 'Merry Coco'].shape[0]/recordCount*100
			my = df[df['favProd'] == 'Malaysiano'].shape[0]/recordCount*100
			hork = df[df['favProd'] == 'Horkasai'].shape[0]/recordCount*100

			#Split Frequent Places and Frequent Halls
			place_split_df = df["fplace"].str.get_dummies(', ')
			place_split_df = place_split_df.astype(bool)
			hall_split_df = df["fhall"].str.get_dummies(', ')
			hall_split_df = hall_split_df.astype(bool)

			#region Checking
			if 'Perpustakaan Sultanah Bahiyah - Universiti Utara Malaysia' not in place_split_df:
				place_split_df['Perpustakaan Sultanah Bahiyah - Universiti Utara Malaysia'] = False

			if 'V Mall' not in place_split_df:
				place_split_df['V Mall'] = False

			if 'Pusat Sukan' not in place_split_df:
				place_split_df['Pusat Sukan'] = False

			if 'Pusat Islam' not in place_split_df:
				place_split_df['Pusat Islam'] = False
			
			if 'Pusat Budaya dan Seni' not in place_split_df:
				place_split_df['Pusat Budaya dan Seni'] = False

			if 'DKG 1' not in hall_split_df:
				hall_split_df['DKG 1'] = False

			if 'DKG 2' not in hall_split_df:
				hall_split_df['DKG 2'] = False

			if 'DKG 3' not in hall_split_df:
				hall_split_df['DKG 3'] = False

			if 'DKG 4' not in hall_split_df:
				hall_split_df['DKG 4'] = False

			if 'DKG 5' not in hall_split_df:
				hall_split_df['DKG 5'] = False

			if 'DKG 6' not in hall_split_df:
				hall_split_df['DKG 6'] = False

			if 'DKG 7' not in hall_split_df:
				hall_split_df['DKG 7'] = False

			#endregion
		
			#region MAP------------------------------------------------------------------------------------
			data = {
    			'Location': ['Library', 'V Mall', 'Pusat Sukan', 'Pusat Islam', 'Pusat Budaya dan Seni', 
			   				'DKG 1', 'DKG 2', 'DKG 3', 'DKG 4', 'DKG 5', 'DKG 6', 'DKG 7',
							'MAS', 'TNB', 'TRADEWINDS', 'PROTON', 'PETRONAS', 'SIME DARBY', 'TM', 'GRANTT', 'MISC', 'BSN', 'YAB', 'MUAMALAT', 'BANK RAKYAT', 'SME BANK', 'MAYBANK'],
   		 		'Latitude': [6.462972, 6.462539, 6.473491, 6.461906, 6.461495, 
			   				6.465461, 6.464156, 6.465392, 6.467389, 6.457865, 6.455170, 6.453936,
							 6.456091, 6.457634, 6.460471, 6.458505, 6.464994, 6.467904, 6.470430, 6.467619, 6.471283, 6.470623, 6.480729, 6.478711, 6.440971, 6.438396, 6.465441],
    			'Longitude': [100.504900, 100.501821, 100.504494, 100.498968, 100.501383, 
			    			100.508225, 100.507952, 100.505947, 100.507784, 100.506397, 100.506560, 100.499851,
							 100.504581, 100.503320, 100.501957, 100.501337, 100.500432, 100.499799, 100.497466, 100.497960, 100.499431, 100.500520, 100.509316, 100.509208, 100.528213, 100.530656, 100.496061],
    			'Size': [place_split_df['Perpustakaan Sultanah Bahiyah - Universiti Utara Malaysia'].sum(), 
	    	   			place_split_df['V Mall'].sum(), 
						place_split_df['Pusat Sukan'].sum(), 
						place_split_df['Pusat Islam'].sum(), 
						place_split_df['Pusat Budaya dan Seni'].sum(), 
						hall_split_df['DKG 1'].sum(), 
						hall_split_df['DKG 2'].sum(), 
						hall_split_df['DKG 3'].sum(), 
						hall_split_df['DKG 4'].sum(), 
						hall_split_df['DKG 5'].sum(), 
						hall_split_df['DKG 6'].sum(), 
						hall_split_df['DKG 7'].sum(),
						df[df['stay'] == 'MAS'].shape[0],
						df[df['stay'] == 'TNB'].shape[0],
						df[df['stay'] == 'TRADEWINDS'].shape[0],
						df[df['stay'] == 'PROTON'].shape[0],
						df[df['stay'] == 'PETRONAS'].shape[0],
						df[df['stay'] == 'SIME DARBY'].shape[0],
						df[df['stay'] == 'TM'].shape[0],
						df[df['stay'] == 'GRANTT'].shape[0],
						df[df['stay'] == 'MISC'].shape[0],
						df[df['stay'] == 'BSN'].shape[0],
						df[df['stay'] == 'YAB'].shape[0],
						df[df['stay'] == 'MUAMALAT'].shape[0],
						df[df['stay'] == 'BANK RAKYAT'].shape[0],
						df[df['stay'] == 'SME BANK'].shape[0],
						df[df['stay'] == 'MAYBANK'].shape[0]
						]
			}

			dfmap = pd.DataFrame(data)

			figMap = px.scatter_mapbox(dfmap, lat='Latitude', lon='Longitude', color='Size',hover_name='Location', size='Size',
         	               zoom=13, template="plotly_dark", title='Customer Geographic ScatterMap')
			figMap.update_layout(mapbox_style='open-street-map', margin=dict(l=20, r=20, b=50, t=50))
			graphJSONmap = json.dumps(figMap, cls=plotly.utils.PlotlyJSONEncoder)
			#endregion------------------------------------------------------------------------------------

			#region Likert------------------------------------------------------------------------------------
		
			l1 = ['Not At All','Not Likely','Neutral Moderately','Moderately Likely', 'Extremely Likely']
			l245 = ['Very Dissatisfied','Dissatisfied','Neutral','Satisfied','Very Satisfied']
			l3 = ['Extremely Cheap','Cheap','Reasonable','Expensive','Extremely expensive']
			l6 = ['Much Less Favorable','Less Favorable','Neutral','More Favorable','Much More Favorable']
			l7 = ['Very Rarely','Rarely','Neutral','Often','Very Often']
			l8 = ['2 or 3 times a month','Once in a month ','2 or 3 times in a week','Once a week','Everyday']
		
			v1 = [df[df['Q1']==1].shape[0], df[df['Q1']==2].shape[0], df[df['Q1']==3].shape[0], df[df['Q1']==4].shape[0], df[df['Q1']==5].shape[0]]
			v2 = [df[df['Q2']==1].shape[0], df[df['Q2']==2].shape[0], df[df['Q2']==3].shape[0], df[df['Q2']==4].shape[0], df[df['Q2']==5].shape[0]]
			v3 = [df[df['Q3']==1].shape[0], df[df['Q3']==2].shape[0], df[df['Q3']==3].shape[0], df[df['Q3']==4].shape[0], df[df['Q3']==5].shape[0]]
			v4 = [df[df['Q4']==1].shape[0], df[df['Q4']==2].shape[0], df[df['Q4']==3].shape[0], df[df['Q4']==4].shape[0], df[df['Q4']==5].shape[0]]
			v5 = [df[df['Q5']==1].shape[0], df[df['Q5']==2].shape[0], df[df['Q5']==3].shape[0], df[df['Q5']==4].shape[0], df[df['Q5']==5].shape[0]]
			v6 = [df[df['Q6']==1].shape[0], df[df['Q6']==2].shape[0], df[df['Q6']==3].shape[0], df[df['Q6']==4].shape[0], df[df['Q6']==5].shape[0]]
			v7 = [df[df['Q7']==1].shape[0], df[df['Q7']==2].shape[0], df[df['Q7']==3].shape[0], df[df['Q7']==4].shape[0], df[df['Q7']==5].shape[0]]
			v8 = [df[df['Q8']=='Two or three times in a month'].shape[0], df[df['Q8']=='Once in a month'].shape[0], df[df['Q8']=='Two or three times in a week'].shape[0], df[df['Q8']=='Once a week'].shape[0], df[df['Q8']=='Everyday'].shape[0]]

			def multiDonut():
				return dict(l=20, r=20, b=20, t=20)
		
			def holeSize():
				return 0.6
		
			def fontSize():
				return dict(size= 10)

			lik1 = go.Figure(data=[go.Pie(labels = l1, values=v1, hole=holeSize())])
			lik1.update_layout(template="plotly_dark", title='Recommend Quoffe Coffee', margin=multiDonut(), font=fontSize())
			lik2 = go.Figure(data=[go.Pie(labels = l245, values=v2, hole=holeSize())])
			lik2.update_layout(template="plotly_dark", title='Customer Satisfaction', margin=multiDonut(), font=fontSize())
			lik3 = go.Figure(data=[go.Pie(labels = l3, values=v3, hole=holeSize())])
			lik3.update_layout(template="plotly_dark", title='Review on Price', margin=multiDonut(), font=fontSize())
			lik4 = go.Figure(data=[go.Pie(labels = l245, values=v4, hole=holeSize())])
			lik4.update_layout(template="plotly_dark", title='Quoffe Product Quality', margin=multiDonut(), font=fontSize())
			lik5 = go.Figure(data=[go.Pie(labels = l245, values=v5, hole=holeSize())])
			lik5.update_layout(template="plotly_dark", title='Quoffe Customer Service', margin=multiDonut(), font=fontSize())
			lik6 = go.Figure(data=[go.Pie(labels = l6, values=v6, hole=holeSize())])
			lik6.update_layout(template="plotly_dark", title='Changes of Customer Perception', margin=multiDonut(), font=fontSize())
			lik7 = go.Figure(data=[go.Pie(labels = l7, values=v7, hole=holeSize())])
			lik7.update_layout(template="plotly_dark", title='Frequency of Quoffe Promotion', margin=multiDonut(), font=fontSize())
			lik8 = go.Figure(data=[go.Pie(labels = l8, values=v8, hole=holeSize())])
			lik8.update_layout(template="plotly_dark", title='Frequency of Customers Purchase', margin=multiDonut(), font=fontSize())


			likert1 = json.dumps(lik1, cls=plotly.utils.PlotlyJSONEncoder)
			likert2 = json.dumps(lik2, cls=plotly.utils.PlotlyJSONEncoder)
			likert3 = json.dumps(lik3, cls=plotly.utils.PlotlyJSONEncoder)
			likert4 = json.dumps(lik4, cls=plotly.utils.PlotlyJSONEncoder)
			likert5 = json.dumps(lik5, cls=plotly.utils.PlotlyJSONEncoder)
			likert6 = json.dumps(lik6, cls=plotly.utils.PlotlyJSONEncoder)
			likert7 = json.dumps(lik7, cls=plotly.utils.PlotlyJSONEncoder)
			likert8 = json.dumps(lik8, cls=plotly.utils.PlotlyJSONEncoder)
			#endregion------------------------------------------------------------------------------------

			#region BarChart------------------------------------------------------------------------------------

			# Create the trace for the stacked bar chart
			trace1 = go.Bar(
    			x=[df[df['age']=='Below 20 years old'].shape[0], df[df['age']=='20-29 years old'].shape[0], df[df['age']=='30-39 years old'].shape[0], df[df['age']=='40-49 years old'].shape[0], df[df['age']=='50 years old and above'].shape[0]],  # Number of respondents
    			y=['Below 20 years old','20-29 years old','30-39 years old','40-49 years old','50 years old and above'],   # Age groups
    			orientation='h',
			)

			trace2 = go.Bar(
    			x=[df[df['occ']=='Student'].shape[0], df[df['occ']=='Unemployed'].shape[0], df[df['occ']=='Employed'].shape[0]],  # Number of respondents
    			y=['Student','Unemployed','Employed'],   # Age groups
    			orientation='h',
			)

			# Create the layout for the chart
			layout1 = go.Layout(
    			title='Number of Respondents by Age Group',
    			xaxis=dict(title='Number of Respondents'),
    			yaxis=dict(title='Age Group'),
			    template='plotly_dark'
			)

			layout2 = go.Layout(
    			title='Number of Respondents by Occupation',
    			xaxis=dict(title='Number of Respondents'),
    			yaxis=dict(title='Occupation'),
			    template='plotly_dark'
			)

			# Create the figure and plot the chart
			b1 = go.Figure(data=[trace1], layout=layout1)
			b2 = go.Figure(data=[trace2], layout=layout2)
			bar1 = json.dumps(b1, cls=plotly.utils.PlotlyJSONEncoder)
			bar2 = json.dumps(b2, cls=plotly.utils.PlotlyJSONEncoder)


			#endregion

			#region Pies------------------------------------------------------------------------------------

			p1 = ['Friends/ Family','Members/ Colleagues','Social Media','Ads in the mobile app','Newspapers/ Magazines','Online Search']
			pv1 = [df[df['heardFrom']=='Friends/ Family'].shape[0], df[df['heardFrom']=='Members/ Colleagues'].shape[0], df[df['heardFrom']=='Social Media'].shape[0], df[df['heardFrom']=='Ads in the mobile app (excluding social media)'].shape[0], df[df['heardFrom']=='Newspapers/ Magazines'].shape[0], df[df['heardFrom']=='Online Search'].shape[0]]

			p2 = ['Dine in','Take Away']
			pv2 = [df[df['consumption']=='Dine in'].shape[0], df[df['consumption']=='Take Away'].shape[0]]

			p3 = ['Very Loyal','Partially loyal','No loyalty']
			pv3 = [df[df['loyalty']=='Refusing to try others and looking for exactly the same brand you prefer'].shape[0], df[df['loyalty']=='Inclined to replace the one you are looking for with a particular other'].shape[0], df[df['loyalty']=='Buy whatever brand you might find'].shape[0]]

			pie1 = go.Figure(go.Pie(labels=p1, values=pv1), layout=go.Layout(title="How Did You Find Us?", template='plotly_dark'))
			pie2 = go.Figure(go.Pie(labels=p2, values=pv2), layout=go.Layout(title="Customer Preferred Dining", template='plotly_dark'))
			pie3 = go.Figure(go.Pie(labels=p3, values=pv3), layout=go.Layout(title="Brand Loyalty", template='plotly_dark'))

			pies1 = json.dumps(pie1, cls=plotly.utils.PlotlyJSONEncoder)
			pies2 = json.dumps(pie2, cls=plotly.utils.PlotlyJSONEncoder)
			pies3 = json.dumps(pie3, cls=plotly.utils.PlotlyJSONEncoder)
			#endregion
			flag = True
		except:
			return '<script>alert("Something went wrong! Maybe the csv file inserted was not the correct one! Make sure the csv file is downloaded from the Google Forms Excel Sheet."); window.location="/home";</script>'
	else:

		graphJSONmap = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		bar1 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		bar2 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		likert1 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		likert2 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		likert3 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		likert4 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		likert5 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		likert6 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		likert7 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		likert8 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		pies1 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		pies2 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		pies3 = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		recordCount = 0
		female = 0
		knows = 0
		ori = 0
		coco = 0
		my = 0
		hork = 0
		ori0 = 0
		coco0 = 0
		my0 = 0
		hork0 = 0
		flag = False

	return render_template(
		'home.html', 
		flag=flag, 
		knows=round(knows,1), 
		female=round(female,1),
		ori0 = ori0,
		coco0 = coco0,
		my0 = my0,
		hork0 = hork0,
		ori = round(ori,1),
		coco = round(coco,1),
		my = round(my,1),
		hork = round(hork,1),
		recordCount = recordCount, 
		form=form,
		graphJSONmap=graphJSONmap,
		b1=bar1,
		b2=bar2, 
		l1=likert1,
		l2=likert2,
		l3=likert3,
		l4=likert4,
		l5=likert5,
		l6=likert6,
		l7=likert7,
		l8=likert8,
		p1=pies1,
		p2=pies2,
		p3=pies3)
#-------------------------------------------------------------------------

if __name__ == '__main__':
	app.run(debug=True)