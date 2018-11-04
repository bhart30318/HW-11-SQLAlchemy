################################################################
# 1. import Flask and other dependencies
import datetime as dt
import numpy as np
import pandas as pd

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

################################################################
# 2 Database Setup
engine = create_engine("sqlite:///hawaii.sqlite", echo=False)


Base = automap_base()

Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurements
Station = Base.classes.stations

# Create our session (link) from Python to the DB
session = Session(engine)

################################################################
# 3. Create an app, 
app = Flask(__name__)

################################################################
# 4. Define Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Avalable Routes:<br/><br/><br/>"


        f"/api/v1.0/precipitation<br/>"
        f"- precipitation by dates from prior year<br/>"
        f"<br/>"

        f"/api/v1.0/stations<br/>"
        f"- Return a json list of stations from the dataset.<br/>"
        f"<br/>"
        
        f"/api/v1.0/tobs<br/>"
        f"- Invoice Total for a given country (defaults to 'USA')<br/>"
        f"<br/>"
        
        f"/api/v1.0/startdate/enddate<br/>"
        f"- the minimum average, and the max temperature for a given start or start-end range.<br/>"
        f"- examples of giving start date: /api/v1.0/2017-01-01<br/>"
        f"- examples of giving start-end date: /api/v1.0/2017-01-01/2017-01-15<br/>"
    )

################################################################
# Query for the dates and temperature observations from the last year.
## Convert the query results to a Dict using date as the key and __prcp__ as the value.
## Return the json representation of your dictionary.

# the lastest date 8/23/2017 as such the last 12 month is from 8-24-2016 to 8-23-2017
YearBeg = dt.datetime(2016,8,23) #set one less date before the year beg date 8/24
YearEnd = dt.datetime(2017,8,24) #set one more date after the year end date 8/23


@app.route("/api/v1.0/precipitation")
def Precipitation():

    # Design a query to pull date and prcp values for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > YearBeg).filter(Measurement.date < YearEnd).all()
     # Unpack the `dates` and `prcp` from results and save into separate lists
    OneYearDates = [r[0] for r in results]
    OneYearPrcp = [r[1] for r in results]

    # Save data in dataframe and set `date` as index
    PrcpbyD = pd.DataFrame({'date':OneYearDates,'precipitation':OneYearPrcp})
    PrcpbyD.set_index('date',inplace=True)
    
    # turn df to  dictionary 
    df_as_json = PrcpbyD.to_dict(orient='split')
    
    #Return the json representation of your dictionary.
    return jsonify({'status': 'ok', 'json_data': df_as_json})

################################################################

@app.route("/api/v1.0/stations")
def Stations():

    #Design a query to return a list of stations.
    result2 = session.query(Station.station, Station.name, Station.latitude,Station.longitude,Station.elevation).statement
    # Save data in dataframe and set "station" as index
    Sls = pd.read_sql_query(result2, session.bind)
    Sls.set_index('station',inplace=True)
    
    # turn df to dict
    df2_as_json = Sls.to_dict(orient='split')
    #Return the json representation of your dictionary.
    return jsonify({'status': 'ok', 'json_data': df2_as_json})

################################################################
@app.route("/api/v1.0/tobs")
def Tobs():

    # Design a query to pull date and tobs values for previous year (last 12 months)
    result3 = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > YearBeg).filter(Measurement.date < YearEnd).statement
    
    # Save data in dataframe and set "date" as index
    Templs = pd.read_sql_query(result3, session.bind)
    #Templs.set_index('date',inplace=True) may or may not need to set the index - optional
    
    # turn df to dict
    df3_as_json = Templs.to_dict(orient='split')
    #Return the json representation of your dictionary.
    return jsonify({'status': 'ok', 'json_data': df3_as_json})

################################################################
#Return a json list of the minimum,average, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def Vacation(start):

    VacaBeg = start #set one less date before the year beg date 7/2

    calc_temp = session.query(func.avg(Measurement.tobs),func.max(Measurement.tobs),func.min(Measurement.tobs)).\
        filter(Measurement.date > VacaBeg).statement

    #write into a dataframe
    TempStat = pd.read_sql_query(calc_temp, session.bind)
    TAve = int(TempStat['avg_1'])
    TMax = int(TempStat['max_1'])
    TMin = int(TempStat['min_1'])
    
    Templist = pd.DataFrame({'Stats': ["Ave_Temp","Max_Temp","Min_Temp"], 'value': [TAve, TMax, TMin]})
    # turn df to dict
    df4_as_json = Templist.to_dict(orient='split')

    #Return the json representation of your dictionary.
    return jsonify({'status': 'ok', 'json_data': df4_as_json})


@app.route("/api/v1.0/<start>/<end>")
def Vacation1(start,end):

    VacaBeg1 = start #set one less date before the year beg date 7/2
    VacaEnd1 = end #set one less date before the year beg date 7/15

    calc_temp1 = session.query(func.avg(Measurement.tobs),func.max(Measurement.tobs),func.min(Measurement.tobs)).\
        filter(Measurement.date > VacaBeg1).filter(Measurement.date < VacaEnd1).statement

    #write into a dataframe
    TempStat1 = pd.read_sql_query(calc_temp1, session.bind)
    TAve1 = int(TempStat1['avg_1'])
    TMax1 = int(TempStat1['max_1'])
    TMin1 = int(TempStat1['min_1'])
    
    Templist1 = pd.DataFrame({'Stats': ["Ave_Temp","Max_Temp","Min_Temp"], 'value': [TAve1, TMax1, TMin1]})
    # turn df to dict
    df5_as_json = Templist1.to_dict(orient='split')

    #Return the json representation of your dictionary.
    return jsonify({'status': 'ok', 'json_data': df5_as_json})









################################################################

if __name__ == "__main__":
    app.run(debug=True)