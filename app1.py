# 1. Dependencies
import numpy as np
import sqlalchemy
import datetime as dt
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# 2. Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# 3. Reflect an existing database into a new model
Base = automap_base()

# 4. Reflect the tables
Base.prepare(engine, reflect=True)

# 5. Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# 6. Create the app
app = Flask(__name__)

# 7. Define the home route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return(
        f"Welcome to the 'Home' page of the climate app!<br/>"
        f'The available routes are:<br/>'
        f'/api/v1.0/about<br/>'
        f'/api/v1.0/station<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/[enter start_date or start_date/end_date]<br/>'
        f'Note the date format to be used is mm-dd-yyyy and use / if entering an end date'
    )

# 8. Define the /about route
@app.route("/api/v1.0/about")
def about():
    print("Server received request for 'About' page...")
    return "This app was designed to return climate date for weather stations"

# 5. Define the /station route
@app.route("/api/v1.0/station")
def station_names():
    print("Server received request for 'station' page...")
    # Create our session (link) from Python to the DB
    session = Session(engine)

    stations = session.query(Station.station).all()
    # * Return a JSON list of stations from the dataset
    return jsonify(stations)
    
# 6. Define the /precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    print("Server received request for 'precipitation' page...")
    
    # Create a variable for the last twelve months

    precip = []

    # Starting from the most recent data point in the database, calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23)
    year_prior = query_date - dt.timedelta(days=365)

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    last_year = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date < query_date).filter(Measurement.date > year_prior).all()

    # Append query data to the variable; look at the first 10 elements of the list of tubles
    for data in last_year:
        precip.append(data)

    # convert tuple to dictionary using date as key and precipitation as value
    precip_dict = dict(precip)

    # Return jsonified list
    return jsonify(precip_dict)

# 7. Define the /tobs route
@app.route("/api/v1.0/tobs")
def tobs_all():
    print("Server received request for 'tobs' page...")
        # Create a variable for the last twelve months

    tobs = []

    # Starting from the most recent data point in the database, calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23)
    year_prior = query_date - dt.timedelta(days=365)

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    tobs_year = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date < query_date).\
    filter(Measurement.date > year_prior).\
    filter(Measurement.station =='USC00519281').all()

    # Append query data to the variable; look at the first 10 elements of the list of tubles
    for temps in tobs_year:
        tobs.append(temps)

    # convert tuple to dictionary using date as key and precipitation as value
    tobs_dict = dict(tobs)

    # Return jsonified list
    return jsonify(tobs_dict)

# 8. Define the /tobs route with start date provided
@app.route("/api/v1.0/<start>")
def tobs_start(start):
    print("Server received request for 'start' page...")
    # Assign start date to a variable
    month, day, year = start.split('-')

    start_date = dt.date(int(year),int(month),int(day))
    query_date = dt.date(2017, 8, 23)

    # Create our session (link) from Python to the DB
    session = Session(engine)

    low_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date > start_date).\
        filter(Measurement.date < query_date).all()
    
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date > start_date).\
        filter(Measurement.date < query_date).all()

    sum_temp = session.query(Measurement.tobs, func.sum(Measurement.tobs)).filter(Measurement.date > start_date).\
        filter(Measurement.date < query_date).all()

    count_temp = session.query(Measurement.tobs, func.count(Measurement.tobs)).filter(Measurement.date > start_date).\
        filter(Measurement.date < query_date).all()

    avg_temp = round(sum_temp[0][1]/count_temp[0][1],1)

    temp_data = [
    {"start_date": start_date},
    {"end_date": query_date},
    {"low_temp": low_temp},
    {"high_temp": max_temp},
    {"avg_temp": avg_temp}
    ]

    return jsonify(temp_data)

# 9. Define the /tobs route with start and end dates provided
@app.route("/api/v1.0/<start>/<end>")
def tobs_start_stop(start,end):
    print("Server received request for 'start' page...")
     # Assign start date to a variable
    s_month, s_day, s_year = start.split('-')
    d_month, d_day, d_year = end.split('-')

    start_date = dt.date(int(s_year),int(s_month),int(s_day))
    end_date = dt.date(int(d_year),int(d_month),int(d_day))

    # Create our session (link) from Python to the DB
    session = Session(engine)

    low_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date > start_date).\
        filter(Measurement.date < end_date).all()
    
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date > start_date).\
        filter(Measurement.date < end_date).all()

    sum_temp = session.query(Measurement.tobs, func.sum(Measurement.tobs)).filter(Measurement.date > start_date).\
        filter(Measurement.date < end_date).all()

    count_temp = session.query(Measurement.tobs, func.count(Measurement.tobs)).filter(Measurement.date > start_date).\
        filter(Measurement.date < end_date).all()

    avg_temp = round(sum_temp[0][1]/count_temp[0][1],1)

    temp_data = [
    {"start_date": start_date},
    {"end_date": end_date},
    {"low_temp": low_temp},
    {"high_temp": max_temp},
    {"avg_temp": avg_temp}
    ]

    return jsonify(temp_data)

if __name__ == "__main__":
    app.run(debug=True)

