import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from flask import request


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
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start>"
    )


@app.route("/api/v1.0/precipitation")
def precipitations():
	"""Query for the dates and temperature observations from the last year.
	Convert the query results to a Dictionary using date as the key and prcp as the value.
	Return the JSON representation of your dictionary."""
	measurements_prcp = session.query(Measurement)
	max_date = dt.datetime(2010,1,1)

	# NOTE: I considered the last 12 months to be the last 12 months of data stored
	# within the database

	# first determine the date range that should be considered as the last 12 months
	for measurement in measurements_prcp:
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
	prcp_list = []
	for measurement in measurements_prcp:
	# check to see if date for current db row is within the last 12 months
		current_year = int(measurement.date.split("-")[0])
		current_month = int(measurement.date.split("-")[1])
		current_day = int(measurement.date.split("-")[2])
		current_date = dt.datetime(current_year, current_month, current_day)
		# if current_date is less than or equal to max_date but greater than or equal to
		# min_date then it is within the range
		if current_date >= min_date and current_date <= max_date:
			date_list.append(str(current_date))
			prcp_list.append(measurement.prcp)

	# create dictionary of dates and tobs
	prcp_dictionary = dict(zip(date_list, prcp_list))

	return jsonify(prcp_dictionary)

@app.route("/api/v1.0/stations")
def stations():
	"""Return a JSON list of stations from the dataset."""
	stations = session.query(Station)
	measurements_stat = session.query(Measurement)

	# What are the most active stations?
	# List the stations and observation counts in descending order.
	station_list = []
	observation_count_list = []
	for station in stations:
	    station_list.append(station.station)
	    current_observation_count = measurements_stat.filter_by(station = station.station).count()
	    observation_count_list.append(current_observation_count)

	# create dictionary of the stations and their observation counts
	stations_dictionary = dict(zip(station_list, observation_count_list))

	return jsonify(stations_dictionary)

@app.route("/api/v1.0/tobs")
def tobs():
	"""Return a JSON list of Temperature Observations (tobs) for the previous year."""
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

@app.route("/api/v1.0/start_date/<start>")
def starts(start):
	"""Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
	When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
	# since no end date given set end date to arbitrary point way in the future
	end_date = dt.datetime(2200,1,1)
	# set the start date equal to the date provided in the route
	#start_date = request.args['start']
	start_date = start

	# calculate the minimum, average and maximum temps for the range provided
	start_temps = calc_temps(start_date, end_date)
	temperature_minimum = float(str(start_temps[0]).split(",")[0][-len(str(start_temps[0]).split(",")[0])+1:])
	temperature_average = float(str(start_temps[0]).split(",")[1][-len(str(start_temps[0]).split(",")[1])+1:])
	temperature_maximum = float(str(start_temps[0]).split(",")[2][-len(str(start_temps[0]).split(",")[2])+1:]\
	[:len(str(start_temps[0]).split(",")[2][-len(str(start_temps[0]).split(",")[2])+1:])-1])

	# create dictionary of the temperatures
	temp_dictionary = {"minimum_temp":str(temperature_minimum),"average_temperature":str(temperature_average),"maximum_temperature":str(temperature_maximum)}

	return jsonify(temp_dictionary)



def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
"""/api/v1.0/<start> and /api/v1.0/<start>/<end>


Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""


if __name__ == '__main__':
    app.run(debug=True)
