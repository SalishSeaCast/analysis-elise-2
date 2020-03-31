The links below are to static renderings of the notebooks via
[nbviewer.jupyter.org](https://nbviewer.jupyter.org/).
Descriptions under the links below are from the first cell of the notebooks
(if that cell contains Markdown or raw text).

* [albedo-FirstLook.ipynb](https://nbviewer.jupyter.org/github/SalishSeaCast/analysis-elise-2/blob/master/notebooks/PARPaper/albedo-FirstLook.ipynb)  
    
    In this notebook I will compare the above and below surface PAR measurements made in the Fraser plume to turbidity using a very simple model- assume that above surface PAR is S0, and below surface par is S0*(1-alpha). This may not be accurate. May need to account for reflected light due to spherical sensor; should probably talk to Rich about interpretation.  
      
    Also ignoring directionality; this is probably ok in very turbid waters but not in upper water column if turbidity is low  

* [createDBfromSTRATOGEM-Final.ipynb](https://nbviewer.jupyter.org/github/SalishSeaCast/analysis-elise-2/blob/master/notebooks/PARPaper/createDBfromSTRATOGEM-Final.ipynb)  
    
    Objectives:  
    - Read STRATOGEM CTD and bottle data into tables (sql)  
    - Match each bottle station with a ctd cast  
    - remove/correct questionable data following load_all.m  
    - match bottle profile entries with ctd profile entries  
    - load all data into new combined tables  
      
        1) matched CTD/Bottle stations, profiles:  
            a) all ctd data as well as matched bottle data where available  
            b) any bottle profiles with no ctd  
              
        2) any unmatched bottle stations and their profile entries  
          
        3) any unmatched ctd stations and their profile entries  
         
    - export to multi-source database  

* [deriveTurbLightAttenRelationship.ipynb](https://nbviewer.jupyter.org/github/SalishSeaCast/analysis-elise-2/blob/master/notebooks/PARPaper/deriveTurbLightAttenRelationship.ipynb)  
    
    - remove chl signal from XMIS based on STRATOGEM data  
    - apply fit to FRP data and calculate relationship of turbidity to residuals  
    - apply that fit to STRATOGEM data and inspect characteristics  

* [verifyCreateDBfromSTRAGOGEM_py37.ipynb](https://nbviewer.jupyter.org/github/SalishSeaCast/analysis-elise-2/blob/master/notebooks/PARPaper/verifyCreateDBfromSTRAGOGEM_py37.ipynb)  
    
    Run this code after running createDBfromSTRATOGEM-Final but modifying database name to STRAGOGEM2  


##License

These notebooks and files are copyright 2013-2020
by the Salish Sea MEOPAR Project Contributors
and The University of British Columbia.

They are licensed under the Apache License, Version 2.0.
https://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.
