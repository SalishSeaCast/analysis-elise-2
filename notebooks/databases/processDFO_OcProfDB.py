import sqlalchemy
from sqlalchemy import create_engine, Column, String, Integer, Float, MetaData, Table, type_coerce, ForeignKey, case
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

def main():

    # definitions
    basepath='/ocean/shared/SalishSeaCastData/DFO/BOT/'
    dbname='DFO_OcProfDB'
    # if PRISM.sqlite does not exist, exit
    if not isfile(basepath + dbname + '.sqlite'):
        print('ERROR: ' + dbname + '.sqlite does not exist')
        return

    engine = create_engine('sqlite:///' + basepath + dbname + '.sqlite', echo = False)
    Base=declarative_base(engine)

    #if JDFLocsTBL or CalcTBL already exists, drop (delete) it
    # placement here ensures they will not be reflected 
    # full table deletion facilitates changes to schema as needed through this script
    connection=engine.connect()
    if engine.dialect.has_table(connection,'JDFLocsTBL'):
        # delete existing JDFLocsTBL
        connection.execute('DROP TABLE JDFLocsTBL')
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

    # create JDFLocsTBL to identify rows in Strait of Juan de Fuca
    class JDFLocs(Base):
            __table__=Table('JDFLocsTBL', Base.metadata,
                        Column('ObsID', Integer, primary_key=True),
                        Column('StationID', Integer, ForeignKey('StationTBL.ID')))

    # Next, Construct Table CalcTBL to store data transformations not easily reproduced in queries 
    # (ie unit conversions using complex functions such as gsw TEOS-10 library)
    class Calcs(Base):
            __table__=Table('CalcsTBL', Base.metadata,
                        Column('ObsID', Integer, primary_key=True),
                        Column('StationID', Integer, ForeignKey('StationTBL.ID')),
                        Column('Z_from_p', Float),
                        Column('Oxygen_umolL', Float),
                        Column('Oxygen_Dissolved_umolL', Float),
                        Column('Oxygen_Dissolved_SBE_umolL', Float),
                        Column('Salinity_Bottle_SA', Float),
                        Column('Salinity_SA', Float),
                        Column('Salinity_T0_C0_SA', Float),
                        Column('Salinity_T1_C1_SA', Float),
                        Column('Salinity__Unknown_SA', Float),
                        Column('Salinity__Pre1978_SA', Float),
                        Column('Temperature_CT', Float),
                        Column('Temperature_Primary_CT', Float),
                        Column('Temperature_Secondary_CT', Float),
                        Column('Temperature_Reversing_CT', Float))
    Base.metadata.create_all(engine)

    # Insert data in JDFLocsTBL based on SQL query
    connection = engine.connect()
    connection.execute(" INSERT INTO JDFLocsTBL (ObsID, StationID) \
                        SELECT ObsTBL.ID, ObsTBL.StationTBLID \
                        FROM ObsTBL JOIN StationTBL ON ObsTBL.StationTBLID=StationTBL.ID \
                        WHERE StationTBL.Lat BETWEEN 48.2 AND  48.8 \
                        AND StationTBL.Lon BETWEEN -125.2 AND -124.2;")
    connection.close()

    # One to one relationship from ObsTBL to CalcTBL: create records and insert IDs
    connection = engine.connect()
    connection.execute(" INSERT INTO CalcsTBL (ObsID, StationID) \
                        SELECT ObsTBL.ID, ObsTBL.StationTBLID \
                        FROM ObsTBL;")
    connection.close()

    session = create_session(bind = engine, autocommit = False, autoflush = True)

    def Ox_mLL_to_umolO2L(Ox_mLL):
        #1 ml = 1 ml * (1 l / 10^3 ml) * (1 mol O2 / 22.391 l) * (10^6 umol / mol) = (10^3/22.391) umol
        return 10**3/22.391*Ox_mLL

    def Ox_mgL_to_umolO2L(Ox_mgL):
        # 1 mg O2 = 1 mg O2 * (1 g / 10^3 mg) * (1 mol O2 / 31.998 g) * (10^6 umol / mol) = (10^3/31.998) umol
        return 10**3/31.998*Ox_mgL

    def Ox_umolkg_to_umolO2L(Ox_umolkg, S, T, press, lon, lat):
        # if density rho is in kg/L, 1 umol/kg = 1 umol/kg * (rho kg/L) = rho umol/L
        # treat ppt as practical salinity; virtually the same
        # gsw.SA_from_SP(SP,p,long,lat), gsw.rho(SA,t,p)
        SA=gsw.SA_from_SP(S,press,lon,lat)
        rho=gsw.rho(SA,T,press)
        return rho*Ox_umolkg

    def Sal_PSU_to_SA(S,press,lon,lat):
        SA=gsw.SA_from_SP(S,press,lon,lat)
        if SA>=40:
            SA=None
        return(SA)

    def T_to_CT(SA,T,press):
        CT=gsw.CT_from_t(SA,T,press)
        return(CT)
    
    def Z_from_p(press,lat):
        Z=-1.0*gsw.z_from_p(press,lat)
        return(Z)
    
    Press=case([(Obs.Pressure!=None, Obs.Pressure)], else_=Obs.Pressure_Reversing)

    Sal=case([(Obs.Salinity_Bottle!=None, Obs.Salinity_Bottle)], else_=
             case([(Obs.Salinity_T0_C0!=None, Obs.Salinity_T0_C0)], else_=
             case([(Obs.Salinity_T1_C1!=None, Obs.Salinity_T1_C1)], else_=
             case([(Obs.Salinity!=None, Obs.Salinity)], else_=
             case([(Obs.Salinity__Unknown!=None, Obs.Salinity__Unknown)], else_=Obs.Salinity__Pre1978)
            ))))

    Tem=case([(Obs.Temperature!=None, Obs.Temperature)], else_=
             case([(Obs.Temperature_Primary!=None, Obs.Temperature_Primary)], else_=
             case([(Obs.Temperature_Secondary!=None, Obs.Temperature_Secondary)], else_=Obs.Temperature_Reversing)))

    def convertZ(ObsColIn,CalcColOut):
        for ID, press, lat in session.query(Obs.ID, ObsColIn, Station.Lat).\
                    select_from(Obs).\
                    join(Station, Station.ID==Obs.StationTBLID).\
                    filter(and_(
                        ObsColIn!=None,
                        Station.Lat!=None)).all():
            calcRec=session.query(Calcs).filter(Calcs.ObsID==ID).one()
            setattr(calcRec,CalcColOut,Z_from_p(press,lat))
        session.commit()

    convertZ(Press,'Z_from_p')

    def convertSal(ObsColIn,CalcColOut):
        for ID, S, press, z, lon, lat in session.query(Obs.ID, ObsColIn, Press, Obs.Depth, Station.Lon, Station.Lat).\
                    select_from(Obs).\
                    join(Station, Station.ID==Obs.StationTBLID).\
                    filter(and_(
                        ObsColIn!=None,
                        or_(Press!=None,Obs.Depth!=None),
                        Station.Lon!=None,
                        Station.Lat!=None)).all():
            pp = press if press !=None else gsw.p_from_z(z,lat)
            calcRec=session.query(Calcs).filter(Calcs.ObsID==ID).one()
            setattr(calcRec,CalcColOut,Sal_PSU_to_SA(S,pp,lon,lat))
        session.commit()

    convertSal(Obs.Salinity_Bottle,'Salinity_Bottle_SA')
    convertSal(Obs.Salinity,'Salinity_SA')
    convertSal(Obs.Salinity_T0_C0,'Salinity_T0_C0_SA')
    convertSal(Obs.Salinity_T1_C1,'Salinity_T1_C1_SA')
    convertSal(Obs.Salinity__Unknown,'Salinity__Unknown_SA')
    convertSal(Obs.Salinity__Pre1978,'Salinity__Pre1978_SA')

    SAbs=case([(Calcs.Salinity_Bottle_SA!=None, Calcs.Salinity_Bottle_SA)], else_=
             case([(Calcs.Salinity_T0_C0_SA!=None, Calcs.Salinity_T0_C0_SA)], else_=
             case([(Calcs.Salinity_T1_C1_SA!=None, Calcs.Salinity_T1_C1_SA)], else_=
             case([(Calcs.Salinity_SA!=None, Calcs.Salinity_SA)], else_=
             case([(Calcs.Salinity__Unknown_SA!=None, Calcs.Salinity__Unknown_SA)], else_=Calcs.Salinity__Pre1978_SA)
            ))))

    def convertTem(ObsColIn,CalcColOut):
        for ID, SA, T, press, z, lat in session.query(Obs.ID, SAbs, ObsColIn, Press, Obs.Depth, Station.Lat).\
                    select_from(Station).\
                    join(Obs, Obs.StationTBLID==Station.ID).join(Calcs,Calcs.ObsID==Obs.ID).\
                    filter(and_(
                        ObsColIn!=None,
                        SAbs!=None,
                        or_(Press!=None,Obs.Depth!=None))).all():
            pp = press if press !=None else gsw.p_from_z(z,lat)
            calcRec=session.query(Calcs).filter(Calcs.ObsID==ID).one()
            setattr(calcRec,CalcColOut,T_to_CT(SA,T,pp))
        session.commit()

    convertTem(Obs.Temperature,'Temperature_CT')
    convertTem(Obs.Temperature_Primary,'Temperature_Primary_CT')
    convertTem(Obs.Temperature_Secondary,'Temperature_Secondary_CT')
    convertTem(Obs.Temperature_Reversing,'Temperature_Reversing_CT')

    # define function to convert O2 from arbitrary units to umol/L:
    def convertOx(ObsColIn, ObsColInUnits, CalcColOutStr):
        for ID, Ox, OxU, press, S, T, lon, lat in \
            session.query(Obs.ID, ObsColIn, ObsColInUnits, Press, Sal, Tem, Station.Lon, Station.Lat).\
                    select_from(Obs).\
                    join(Station, Station.ID==Obs.StationTBLID).\
                    filter(or_(
                            and_(
                                ObsColIn!=None,
                                ObsColInUnits=='umol/kg',
                                Press!=None,
                                Sal!=None,
                                Tem!=None,
                                Station.Lon!=None,
                                Station.Lat!=None),
                            and_(
                                ObsColIn!=None,
                                ObsColInUnits!=None,
                                ObsColInUnits!='umol/kg'))).all():
            calcRec=session.query(Calcs).filter(Calcs.ObsID==ID).one()
            if (OxU=='ml/l' or OxU=='mL/L'):
                outval=Ox_mLL_to_umolO2L(float(Ox))
            elif OxU=='mg/l':
                outval=Ox_mgL_to_umolO2L(float(Ox))
            elif OxU=='umol/kg':
                outval=Ox_umolkg_to_umolO2L(float(Ox), float(S), float(T), float(press), float(lon), float(lat))
            elif OxU=='mmol/m**3':
                outval=float(Ox)
            else:
                print('ERROR: OxU=',OxU)
            setattr(calcRec,CalcColOutStr,outval)
        session.commit()

    convertOx(Obs.Oxygen, Obs.Oxygen_units, 'Oxygen_umolL')
    convertOx(Obs.Oxygen_Dissolved, Obs.Oxygen_Dissolved_units, 'Oxygen_Dissolved_umolL')
    convertOx(Obs.Oxygen_Dissolved_SBE, Obs.Oxygen_Dissolved_SBE_units, 'Oxygen_Dissolved_SBE_umolL')

    session.close()
    engine.dispose()

if __name__== "__main__":
    main()
