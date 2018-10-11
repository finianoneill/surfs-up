import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        #f"/api/v1.0/stations<br/>"
        #f"/api/v1.0/tobs"
    )


@app.route("/api/v1.0/precipitation")
def names():
	"""Query for the dates and temperature observations from the last year.
	Convert the query results to a Dictionary using date as the key and tobs as the value.
	Return the JSON representation of your dictionary."""
	measurements = session.query(Measurement)
	max_date = dt.datetime(2010,1,1)

	# NOTE: I considered the last 12 months to be the last 12 months of data stored
	# within the database

	# first determine the date range that should be considered as the last 12 months
	for measurement in measurements:
		year = int(measurement.date.split("-")[0])
		month = int(measurement.date.split("-")[1])
		day = int(measurement.date.split("-")[2])
		# calculate the max date
		if dt.datetime(year,month,day) > max_date:
			max_date = dt.datetime(year,month,day)

	min_date = max_date - dt.timedelta(365)
	# loop back through the data and store the precipitation data (column 'prcp') 
	# and date for the last 12 months prior to the max date in the dataset
	date_list = []
	tobs_list = []
	for measurement in measurements:
	# check to see if date for current db row is within the last 12 months
		current_year = int(measurement.date.split("-")[0])
		current_month = int(measurement.date.split("-")[1])
		current_day = int(measurement.date.split("-")[2])
		current_date = dt.datetime(current_year, current_month, current_day)
		# if current_date is less than or equal to max_date but greater than or equal to
		# min_date then it is within the range
		if current_date >= min_date and current_date <= max_date:
			date_list.append(str(current_date))
			tobs_list.append(measurement.tobs)

	# create dictionary of dates and tobs
	tobs_dictionary = dict(zip(date_list, tobs_list))

	return jsonify(tobs_dictionary)


if __name__ == '__main__':
    app.run(debug=True)
