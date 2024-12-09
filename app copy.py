from flask import Flask, render_template , request, redirect, url_for, flash, redirect
from urllib.parse import urljoin
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename

import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.io as pio
pio.templates
import matplotlib.pyplot as plt
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
	return redirect(url_for('home'))

@app.route('/home', methods=['POST','GET'])
def home():

	form = UploadFileForm()

	if form.validate_on_submit():
		file = form.file.data
		# Perform data cleaning using pandas or other libraries
		df = pd.read_csv(file)
		#df=pd.read_csv("df_arabica_clean.csv")
		df.drop(["Unnamed: 0", "ID"], inplace=True, axis=1)
		df.rename(columns={"Country of Origin": "Country", "Farm Name": "Farm_Name", "Lot Number": "Lot_Number",
			   "ICO Number": "ICO_Number", "Total Cup Points": "Total_Cup_Points", "Moisture Percentage": "Moisture_Percentage",
			   "Category Two Defects": "Category_Two_Defects", "Certification Body": "Certification_Body", "Certification Address": "Certification_Address", "Certification Contact": "Certification_Contact"},  inplace=True)
	   	# Extract the "job title" column
		Country = df['Country']
		Cat2Def = df['Category_Two_Defects']

    	# Calculate the frequency of each job title
		Country = Country.value_counts()
		Cat2Def = Cat2Def.value_counts()

		# Extract the top 20 most frequent job titles
		top_20_titles = Country.head(20)
		top_10_country = Cat2Def.head(10)

		# Create a DataFrame for the top 20 titles
		top_20_df = pd.DataFrame({'Country Title': top_20_titles.index, 'Count': top_20_titles.values})
		top_10_country = pd.DataFrame({'Country title' : top_10_country.index, 'Count': top_10_country.values})

		# MAP STUFF
			
		data = {
    		'Location': ['DKG 4', 'DKG 6', 'V-Mall', 'Library'],
    		'Latitude': [6.467116, 6.454923, 6.462539, 6.463089],
    		'Longitude': [100.507520, 100.506524, 100.501821, 100.505237],
    		'Size': [13, 5, 8, 2]
		}

		dfmap = pd.DataFrame(data)

		figMap = px.scatter_mapbox(dfmap, lat='Latitude', lon='Longitude', hover_name='Location', size='Size',
                        zoom=13, height=500, template="plotly_dark")
		figMap.update_layout(mapbox_style='open-street-map')
		graphJSONmap = json.dumps(figMap, cls=plotly.utils.PlotlyJSONEncoder)
		
		figone = px.bar(top_20_df, x="Count", y="Country Title", title="Top 20 Most Frequent Country Titles", template="plotly_dark")
		graphJSONone = json.dumps(figone, cls=plotly.utils.PlotlyJSONEncoder)
    
		figpie = px.pie(top_10_country, values='Count',title="Top 20 Most Frequent Country Titles", template="plotly_dark")
		graphJSONpie = json.dumps(figpie, cls=plotly.utils.PlotlyJSONEncoder)

	else:
		graphJSONone = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		graphJSONpie = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)
		graphJSONmap = json.dumps({}, cls=plotly.utils.PlotlyJSONEncoder)

	return render_template('home.html', form=form, graphJSONone=graphJSONone, graphJSONtwo=graphJSONpie, graphJSONmap=graphJSONmap)
#-------------------------------------------------------------------------

@app.route('/uploadPage')
def uploadPage():
	return render_template('uploadPage.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the uploaded file from the form
        file = request.files['file']

        # Process the CSV file
        if file and file.filename.endswith('.csv'):
            csv_data = csv.reader(file)
	    
        cur = mysql.connection.cursor()
        cur.execute ("INSERT INTO records (file) VALUES (%s)", csv_data)
        mysql.connection.commit()
        return redirect(url_for('uploadPage'))	


if __name__ == '__main__':
	app.run(debug=True)