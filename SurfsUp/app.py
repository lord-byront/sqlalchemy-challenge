# Import the dependencies.

 # Ignore SQLITE warnings related to Decimal 
import warnings
warnings.filterwarnings('ignore')

 # Import Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
import numpy as np
import datetime as dt
from flask import Flask, jsonify




print("working")
#################################################
# Database Setup


engine = create_engine("sqlite:///Resources/hawaii.sqlite")


#################################################


# reflect an existing database into a new model

Base = automap_base()



# reflect the tables

Base.prepare(autoload_with=engine)



# Save references to each table
print(Base.classes.keys())
Station = Base.classes.station
Measurement = Base.classes.measurement


# Create our session (link) from Python to the DB

session = Session(bind=engine)


#################################################
# BY
#################################################
## This lines creates the date for the query
# Starting from the most recent data point in the database. 
last_date = session.query(Measurement.date).order_by((Measurement.date).desc()).first()
new_date = last_date[0] #extrats the date from the tuple
year, month, day = map(int, new_date.split('-')) #splits the date and maps into an object
date_object = dt.datetime(year, month, day) #define as date object


# Calculate the date one year from the last date in data set.
year_ago = date_object - dt.timedelta(days=365) #creates a date for a year ago


# Perform a query to retrieve the data and precipitation scores
last_12_months = session.query(Measurement.station,Measurement.date,Measurement.prcp,Measurement.tobs).filter(Measurement.date > year_ago)
#################################################
# BY
#################################################




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
        f"<b>Available Routes:</b><br/><br/>"
        f"<b>/api/v1.0/precipitation/yyyy-mm-dd</b> <br/> Lets you check temperature and station that got data for that day <br/> (Only available for the last 12 months of the dataset)<br/><br/> "
        f"<b>/api/v1.0/precipitation/dates</b> <br/> this shows all available dates in the dataset<br/><br/>"
        f"<b>/api/v1.0/stations</b> <br/> this shows all available info about stations<br/><br/>"
        f"<b>/api/v1.0/tobs</b> <br/> Query the dates and temperature observations of the most-active station for the previous year of data.<br/><br/>"
        f"<b>/api/v1.0/start and /api/v1.0/start/end</b> <br/> Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.<br/><br/>"

    )




@app.route("/api/v1.0/precipitation/dates")
def dates():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    all_dates = list(np.ravel(results))

    return jsonify(all_dates)


@app.route("/api/v1.0/precipitation/<datex>")
def datex(datex):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Measurement.date,Measurement.tobs,  Measurement.station).filter(Measurement.date == datex).filter(Measurement.date > year_ago).all()

    session.close()

    if results == []:
         return jsonify({"error": f"The date: {datex} was not found in the last 12 months of the available data, please check /api/v1.0/precipitation/dates and review which dates are available for the las 12 months of the dataset ."}), 404

    # Convert list of tuples into normal list
    all_dates_result = list(np.ravel(results))

    return jsonify(all_dates_result)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()

    session.close()


    # Convert list of tuples into normal list
    all_results = list(np.ravel(results))

    return jsonify(all_results)


@app.route("/api/v1.0/tobs")
def tobsu():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    stations_u = session.query(Station.station)

    counting = []

    for station_line in stations_u:
        recount = session.query(Measurement.station).filter(Measurement.station == station_line[0]).count()
        counting.append((station_line[0],recount))

    sorted_data = sorted(counting, key=lambda x: x[1], reverse=True)

    most_actvive = sorted_data[0][0]



    results = session.query(Measurement.date,Measurement.tobs,Measurement.station).filter(Measurement.date > year_ago).filter(Measurement.station == most_actvive).all()

    session.close()


    # Convert list of tuples into normal list
    all_results = list(np.ravel(results))

    return jsonify(all_results)




@app.route("/api/v1.0/<startx>/<endx>")
def averages(startx,endx):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    if endx == "":
        endx = date_object

    
    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date > startx).filter(Measurement.date < endx).all()

    session.close()

    if None in results[0]:
         return jsonify({"error": f"The date you selected as a start: {startx} is greater than our data set, greater than end date,  or an incorrect value type, please try YYYY-MM-DD format. Also you might be setting the end date {endx} as an inferior value of the start date."}), 404



    # Convert list of tuples into normal list
    all_results = list(np.ravel(results))

    return jsonify(all_results)



@app.route("/api/v1.0/<startx>")
def averagestart(startx):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    endx = date_object

    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date > startx).filter(Measurement.date < endx).all()

    session.close()

    if None in results[0]:
         return jsonify({"error": f"The date you selected as a start: {startx} is greater than our data set or an incorrect value type, please try YYYY-MM-DD format"}), 404



    # Convert list of tuples into normal list
    all_results = list(np.ravel(results))

    return jsonify(all_results)



if __name__ == '__main__':
    app.run(debug=True)
