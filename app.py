# Import the dependencies.
from os import close
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the tables
Base = automap_base()
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
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )
# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from today
    prev_year = dt.date.today() - dt.timedelta(days=365)

    # Query the precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    
    session.close()
    # Convert the results to a dictionary and jsonify
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query the list of stations
    results = session.query(Station.station).all()

    # Convert the results to a list and jsonify
    station_list = [station[0] for station in results]
    return jsonify(station_list)

# Define the tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the most recent date
    prev_year = dt.date.today() - dt.timedelta(days=365)

    # Query the temperature observations for the last year from the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= prev_year).\
        filter(Measurement.station == most_active_station).all()

    # Convert the results to a list of dictionaries and jsonify
    tobs_list = [{date: tobs} for date, tobs in results]
    return jsonify(tobs_list)

# Define the date route with start and end parameters
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end=None):
    # Query the temperature data based on start and end dates
    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    # Convert the results to a list of dictionaries and jsonify
    temp_summary = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}
    return jsonify(temp_summary)

if __name__ == '__main__':
    app.run(debug=True)