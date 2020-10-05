# Copyright 2013-2016 The Salish Sea MEOPAR contributors
# and The University of British Columbia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Functions useful when manipulating data or working with databases
"""
import numpy as np
import re
import warnings
import sqlalchemy.types as types
import csv
import string
import datetime as dt
import pytz
import matplotlib.pyplot as plt
import pandas as pd
from salishsea_tools.loadDataFRP import fmtVarName, bindepth

"""------SQLAlchemy classes I use to enter data in databases, replacing bad values with None--------"""
class forceNumeric(types.TypeDecorator):

    impl = types.Float
    def process_bind_param(self, value, dialect):
        try:
            int(float(value))
            #if (int(float(value))==-99 or int(10*float(value))==-99):
            #    value=None
        except:
            value = None
        #if (str(value).startswith('-99') or str(value).startswith('9999')):
        #    value = None
        return value

class forceInt(types.TypeDecorator):

    impl = types.Integer
    def process_bind_param(self, value, dialect):
        try:
            int(value)
            #if int(value)==-99:
            #    value=None
        except:
            value = None
        #if (str(value).startswith('-99') or str(value).startswith('9999')):
        #    value = None
        return value

def isFloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def isNum(s):
    try:
        float(s)
        if s=='NaN':
            return False
        else:
            return True
    except ValueError:
        return False
    except TypeError:
        return False

"""-------useful with pandas dataframes------------"""
class sizeme():
    """ Class to change html fontsize of object's representation
        Allows resizing of pandas dataframes to fit in window
        Source: http://stackoverflow.com/questions/19536817/manipulate-html-module-font-size-in-ipython-notebook
        Usage example: sizeme(pandasdataframe,80,90)
    """
    def __init__(self,ob, size, height=100):
        self.ob = ob
        self.size = size
        self.height = height
    def _repr_html_(self):
        repl_tuple = (self.size, self.height, self.ob._repr_html_())
        return u'<span style="font-size:{0}%; line-height:{1}%">{2}</span>'.format(*repl_tuple)


"""------useful when working with data returned from sqlalchemy queries--------"""
def arNanMean(ar):
    """ function to calculate means of arrays that may be empty without producing empty-slice warning
        ar: array-like (passed to numpy.nanmean)
        if nanmean fails, np.nan is returned; otherwise returns result of numpy.nanmean
    """

    # suppress anticipated 'empty slice' warning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            outvar=np.nanmean(ar)
        except:
            outvar=np.nan
        assert len(w) in [0,1]
        if len(w) == 1:
            assert "Mean of empty slice" in str(w[-1].message)
    return(outvar)

def sampleCorr(x,y):
    """ remove nans and corresponding entry in other array. calculate correlation coefficient.
    """
    xi=np.array(x)
    yi=np.array(y)
    ii=np.logical_and(np.logical_not(np.isnan(xi)),np.logical_not(np.isnan(yi)))
    xi=xi[ii]
    yi=yi[ii]
    xi=xi-np.mean(xi)
    yi=yi-np.mean(yi)

    r=np.sum(xi*yi)/np.sqrt(np.sum(xi**2)*np.sum(yi**2))
    
    return r

"""--------useful when reading data from csv files----------------"""

def pacToUTC(pactime0):
    # input datetime object without tzinfo in Pacific Time and 
    # output datetime object (or np array of them) without tzinfo in UTC
    pactime=np.array(pactime0,ndmin=1)
    if pactime.ndim>1:
        raise Exception('Error: ndim>1')
    out=np.empty(pactime.shape,dtype=object)
    pac=pytz.timezone('Canada/Pacific')
    utc=pytz.utc
    for ii in range(0,len(pactime)):
        itime=pactime[ii]
        loc_t=pac.localize(itime)
        utc_t=loc_t.astimezone(utc)
        out[ii]=utc_t.replace(tzinfo=None)
    return (out[0] if np.isscalar(pactime0) else out)

def dateTimeToDecDay(dtin):
    tdif=dtin-dt.datetime(1900,1,1)
    dd=tdif.days+tdif.seconds/(3600*24)
    return dd

def cXfromX(X,pathlen=0.25):
    X=np.array(X)
    X[np.isnan(X)]=-5
    Y=np.nan*X
    iii=(X>0)&(X<100)
    Y[iii]=-np.log(X[iii]/100.0)/pathlen
    return Y


"""-----------Light-related functions-------------"""
#constant:
#FTUtoNTU=define later


