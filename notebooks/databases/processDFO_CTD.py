import sqlalchemy
from sqlalchemy import create_engine, Column, String, Boolean, Integer, Float, MetaData, Table, type_coerce, ForeignKey, case, update
from sqlalchemy.orm import mapper, create_session, relationship, aliased, Session
from sqlalchemy.ext.declarative import declarative_base
import csv
from sqlalchemy import case
import numpy as np
from sqlalchemy.ext.automap import automap_base
import matplotlib.pyplot as plt
import sqlalchemy.types as types
import numbers
from sqlalchemy.sql import and_, or_, not_, func
from sqlalchemy.sql import select
import os
import glob
import re
from os.path import isfile
import gsw

#def Sal_PSU_to_SA(S,press,lon,lat):
#    if (S==S and press==press and lon==lon and lat==lat):
#        SA=gsw.SA_from_SP(S,press,lon,lat)
#        if SA>=40:
#            #print('Err: SA=',SA,', None entered')
#            SA=sqlalchemy.sql.null()
#        elif SA<0:
#            SA=sqlalchemy.sql.null()
#            #print('Err: SA=',SA,', None entered')
#        elif SA!=SA:
#            SA=sqlalchemy.sql.null()
#    else:
#        SA=sqlalchemy.sql.null()
#    return(SA)
#
#def T_to_CT(S,T,press,lon,lat):
#    if (S==S and T==T and press==press and lon==lon and lat==lat):
#        SA=gsw.SA_from_SP(S,press,lon,lat)
#        CT=gsw.CT_from_t(SA,T,press)
#        if CT>=40:
#            #print('Err: CT=',CT,', None entered')
#            CT=sqlalchemy.sql.null()
#        elif CT<-5:
#            CT=sqlalchemy.sql.null()
#            #print('Err: CT=',CT,', None entered')
#        elif CT!=CT:
#            CT=sqlalchemy.sql.null()
#    else:
#        CT=sqlalchemy.sql.null()
#    return(CT)

def Sal_PSU_to_SA(S,press,lon,lat):
    SA=gsw.SA_from_SP(S,press,lon,lat)
    return(SA)

def T_to_CT(S,T,press,lon,lat):
    SA=gsw.SA_from_SP(S,press,lon,lat)
    CT=gsw.CT_from_t(SA,T,press)
    return(CT)

def p_to_Z(press,lat):
    Z=-1.0*gsw.z_from_p(press,lat)
    return(Z)

def main():

    # definitions
    basedir='/ocean/shared/SalishSeaCastData/DFO/CTD/'
    dbname='DFO_CTD'
    # if db does not exist, exit
    if not isfile(basedir + dbname + '.sqlite'):
        print('ERROR: ' + dbname + '.sqlite does not exist')
        return
    # 1st, set Include=False for all CastAway data and duplicates
    engine0 = create_engine('sqlite:///' + basedir + dbname + '.sqlite', echo = False)
    md=MetaData()
    md.reflect(engine0)
    Base0 = automap_base(metadata=md)
    # reflect the tables in salish.sqlite:
    Base0.prepare()
    # mapped classes have been created
    # existing tables:
    StationTBL0=Base0.classes.StationTBL
    AncillaryTBL0=Base0.classes.AncillaryTBL
    ObsTBL0=Base0.classes.ObsTBL
    session0 = create_session(bind = engine0, autocommit = False, autoflush = True)
    for sID, in session0.query(AncillaryTBL0.StationTBLID).filter(AncillaryTBL0.MODEL=='CastAway').all():
        sta=session0.query(StationTBL0).filter(StationTBL0.ID==sID).one()
        setattr(sta,'Include',False)
    session0.commit()
    for xID, in session0.query(ObsTBL0.ID).select_from(AncillaryTBL0).\
                    join(ObsTBL0, ObsTBL0.StationTBLID==AncillaryTBL0.StationTBLID).\
                    filter(AncillaryTBL0.MODEL=='CastAway').all():
            Rec=session0.query(ObsTBL0).filter(ObsTBL0.ID==xID).one()
            setattr(Rec,'Include',False)
    session0.commit()

    # in case of duplicates, take only one profile entry at each depth
    a1=aliased(StationTBL0)
    a2=aliased(StationTBL0)
    dupsQRY=session0.query(a1.ID.label('ID1'),a2.ID.label('ID2')).select_from(a1).join(a2,and_(
        a1.StartYear==a2.StartYear,
        a1.StartMonth==a2.StartMonth,
        a1.StartDay==a2.StartDay,
        a1.StartHour-a2.StartHour<0.001,
        a1.StartHour-a2.StartHour>-0.001,
        a1.Lat-a2.Lat<0.001,
        a1.Lat-a2.Lat>-0.001,
        a1.Lon-a2.Lon<0.001,
        a1.Lon-a2.Lon>-0.001,
        a1.ID!=a2.ID)).filter(a1.Include==True,a2.Include==True,a1.ID<a2.ID)
    for aID, bID in dupsQRY.all():
        # set include to false for second station entry
        print(aID,bID)
        sRec=session0.query(StationTBL0).filter(StationTBL0.ID==bID).one()
        setattr(sRec,'Include',False)
        # find all depths in ObsTBL records associated with second station entry 
        # that are also present in records associated with first station entry
        # and set their Include to False
        # base depths on pressure because it is present in all records
        zs1=[pp for pp, in session0.query(ObsTBL0.Pressure).filter(ObsTBL0.StationTBLID==aID).all()]
        zs2=[pp for pp, in session0.query(ObsTBL0.Pressure).filter(ObsTBL0.StationTBLID==bID).all()]
        for i2 in zs2:
            if np.min([np.abs(i2-i1) for i1 in zs1])<=0.5:
                oRec=session0.query(ObsTBL0).filter(and_(ObsTBL0.StationTBLID==bID,ObsTBL0.Pressure==i2)).one()
                setattr(oRec,'Include',False)
        # associate all records previously associated with second station entry with first entry
        for obsID, in session0.query(ObsTBL0.ID).filter(ObsTBL0.StationTBLID==bID).all():
            Rec=session0.query(ObsTBL0).filter(ObsTBL0.ID==obsID).one()
            setattr(Rec,'StationTBLID',aID)
        session0.commit()

    session0.close()
    engine0.dispose()

    engine = create_engine('sqlite:///' + basedir + dbname + '.sqlite', echo = False)
    Base=declarative_base(engine)

    #if CalcTBL already exists, drop (delete) it
    # placement here ensures they will not be reflected 
    # full table deletion facilitates changes to schema as needed through this script
    connection=engine.connect()
    if engine.dialect.has_table(connection,'CalcsTBL'):
        # delete existing CalcTBL
        connection.execute('DROP TABLE CalcsTBL')
    connection.close()

    # reflect existing tables, ObsTBL and StationTBL
    class Station(Base):
        __tablename__= 'StationTBL'
        __table_args__= {'autoload':True}

    class Obs(Base):
        __tablename__= 'ObsTBL'
        __table_args__= {'autoload':True}

    # Construct Table CalcTBL to store data transformations not easily reproduced in queries 
    # (ie unit conversions using complex functions such as gsw TEOS-10 library)
    class Calcs(Base):
            __table__=Table('CalcsTBL', Base.metadata,
                        Column('ObsTBLID', Integer, primary_key=True),
                        Column('StationTBLID', Integer, ForeignKey('StationTBL.ID')),
                        Column('Include', Boolean,default=True),
                        Column('Z', Float),
                        Column('Salinity_SA', Float),
                        Column('Salinity_T0_C0_SA', Float),
                        Column('Salinity_T1_C1_SA', Float),
                        Column('Temperature_CT', Float),
                        Column('Temperature_Primary_CT', Float),
                        Column('Temperature_Secondary_CT', Float))
    Base.metadata.create_all(engine)
    
    # One to one relationship from ObsTBL to CalcTBL: create records and insert IDs
    connection = engine.connect()
    connection.connection.create_function("Sal_PSU_to_SA_DB",4,Sal_PSU_to_SA)
    connection.connection.create_function("T_to_CT_DB",5,T_to_CT)
    connection.connection.create_function("p_to_Z_DB",2,p_to_Z)
    connection.execute(""" INSERT INTO CalcsTBL (ObsTBLID, StationTBLID, Include, Z, Salinity_SA, Salinity_T0_C0_SA, Salinity_T1_C1_SA, 
                                                 Temperature_CT, Temperature_Primary_CT,Temperature_Secondary_CT) 
                        SELECT ObsTBL.ID, ObsTBL.StationTBLID, ObsTBL.Include, p_to_Z_DB(ObsTBL.Pressure, StationTBL.Lat) AS aZ,
                        Sal_PSU_to_SA_DB(ObsTBL.Salinity, ObsTBL.Pressure, StationTBL.Lon, StationTBL.Lat) AS aSal,
                        Sal_PSU_to_SA_DB(ObsTBL.Salinity_T0_C0, ObsTBL.Pressure, StationTBL.Lon, StationTBL.Lat) AS aS1,
                        Sal_PSU_to_SA_DB(ObsTBL.Salinity_T1_C1, ObsTBL.Pressure, StationTBL.Lon, StationTBL.Lat) AS aS2,
                        T_to_CT_DB((CASE WHEN ObsTBL.Salinity_T1_C1 IS NOT NULL THEN ObsTBL.Salinity_T1_C1
                                 WHEN ObsTBL.Salinity_T0_C0 IS NOT NULL THEN ObsTBL.Salinity_T0_C0
                                 WHEN ObsTBL.Salinity IS NOT NULL THEN ObsTBL.Salinity
                                 ELSE NULL END), ObsTBL.Temperature, ObsTBL.Pressure, StationTBL.Lon, StationTBL.Lat) as aTem,
                        T_to_CT_DB((CASE WHEN ObsTBL.Salinity_T1_C1 IS NOT NULL THEN ObsTBL.Salinity_T1_C1
                                 WHEN ObsTBL.Salinity_T0_C0 IS NOT NULL THEN ObsTBL.Salinity_T0_C0
                                 WHEN ObsTBL.Salinity IS NOT NULL THEN ObsTBL.Salinity
                                 ELSE NULL END), ObsTBL.Temperature_Primary, ObsTBL.Pressure, StationTBL.Lon, StationTBL.Lat) as aT1,
                        T_to_CT_DB((CASE WHEN ObsTBL.Salinity_T1_C1 IS NOT NULL THEN ObsTBL.Salinity_T1_C1
                                 WHEN ObsTBL.Salinity_T0_C0 IS NOT NULL THEN ObsTBL.Salinity_T0_C0
                                 WHEN ObsTBL.Salinity IS NOT NULL THEN ObsTBL.Salinity
                                 ELSE NULL END), ObsTBL.Temperature_Secondary, ObsTBL.Pressure, StationTBL.Lon, StationTBL.Lat) as aT2 
                        FROM ObsTBL INNER JOIN StationTBL ON ObsTBL.StationTBLID = StationTBL.ID;""")
    connection.close()
    engine.dispose()

if __name__== "__main__":
    main()


