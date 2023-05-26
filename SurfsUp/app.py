# Import the dependencies.
from audioop import avg
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np



#################################################
# Database Setup
#################################################


# Set up database
# reflect an existing database into a new model
# reflect the tables
# Save references to each table
# Create our session (link) from Python to the DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Home route
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-23").all()
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-23").\
        filter(Measurement.station == "USC00519281").all()
    tobs_list = list(np.ravel(results))
    return jsonify(tobs=tobs_list)

# Start route
# Start/End route
@app.route('/api/v1.0/<start>', defaults={'end': None})
@app.route('/api/v1.0/<start>/<end>')
def get_temp_stats(start, end):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if end is None:
        # Find TMIN, TAVG, TMAX for dates >= start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
    else:
        # Find TMIN, TAVG, TMAX for dates between start and end inclusive
        results = session.query(*sel).\
            filter(Measurement.date >= start, Measurement.date <= end).all()

    # Convert result into dictionary
    temperatures = []
    for min_temp, avg_temp, max_temp in results:
        temp_dict = {}
        temp_dict["TMIN"] = min_temp
        temp_dict["TAVG"] = avg_temp
        temp_dict["TMAX"] = max_temp
        temperatures.append(temp_dict)

    return jsonify(temperatures)

if __name__ == '__main__':
    app.run(debug=True)


