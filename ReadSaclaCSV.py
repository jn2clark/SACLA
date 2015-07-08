# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 20:30:35 2015

csv reader for reading in SACLA run data.  Takes in the CSV
that is output from the DAQ which contains the tag numbers for
each shot.  These tag numbers are then used to sort the hdf images
into the data (binned, laser on/off)

@author: jesseclark
"""

import csv
import numpy as np

class SACLA_CSV:
    

    def __init__(self, file_name):
       
        # set the counter
        self.nCounter = 0
        
        # init lists
        self.SCAN_ID = [];
        self.RunNumber = [];
        self.Tagnumber = [];
        self.XFELshutter = [];
        self.LaserShutter = [];
        self.file_name = file_name;
        
        # what column do the motors start at        
        self.nMtrStrt = 5     

        # has the file been read in yet
        self.opened = 0
    
    def Open_CSV(self):
        
        # open csv file
        with open(self.file_name, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in csvreader:
                # get header information
                if self.nCounter == 0:
                    self.Header = row
                    self.nCols = len(row)
                else:    
                    
                    self.SCAN_ID.append(int(row[0]))
                    self.RunNumber.append(int(row[1]))
                    self.Tagnumber.append(int(row[2]))
                    self.XFELshutter.append(int(row[3]))
                    self.LaserShutter.append(int(row[4]))
                                   
                    
                    # motors come after the first 5
                    for mtr in range(self.nMtrStrt,self.nCols):                
                        # need to create the lists for the motors
                        # init the list at the start
                        if self.nCounter == 1:
                            lst_init = 'self.M'+str(mtr)+' = []'
                            exec lst_init
            
                        # now append                        
                        lst_app = 'self.M'+str(mtr)+'.append(int(row[mtr]))'
                        exec lst_app
            
                # increment counter            
                self.nCounter = self.nCounter + 1
        
        # has the file been opened?
        self.opened = 1        
        
        # store total number of data points in the file
        self.nTotalShots = len(self.SCAN_ID)
             
        
    def List_to_Array(self):
        
        # if file has not been opened, open it
        if self.opened != 1:
            self.Open_CSV()
            
        # convert the lists to arrays for easier indexing
        self.aSCAN_ID = np.array(self.SCAN_ID)
        self.aRunNumber = np.array(self.RunNumber)
        self.aTagnumber = np.array(self.Tagnumber)
        self.aXFELshutter = np.array(self.XFELshutter)
        self.aLaserShutter = np.array(self.LaserShutter)
        
        # get total number of x-ray shots from XFEL shutter
        self.nTotalXFELShots = sum(self.aXFELshutter)    
        # get total dark shots 
        self.nTotalDARKShots = self.nTotalShots - self.nTotalXFELShots       
        
        # loop over motors and convert to arrays
        for mtr in range(self.nMtrStrt,self.nCols):   
            arr_init = "self.a"+"M"+str(mtr)+" = np.array(self.M"+str(mtr)+")"
            exec arr_init
            
    def Get_Dark_Laser_Indices(self):
        
        # gets the indices for the darks (background)
        # laser on XFEL on and laser off XFEL off
        # dark indices
        self.iDark = (self.aXFELshutter == 0)
        # laser on image indices
        self.iLaserOn = (self.aLaserShutter == 1) & (self.aXFELshutter == 1)
        # laser off images
        self.iLaserOff = (self.aLaserShutter == 0) & (self.aXFELshutter == 1)
        
        # also get laser on and laser off shots with XFEL on
        self.nTotalXFEL_Laser_on = sum(self.iLaserOn) 
        self.nTotalXFEL_Laser_off = sum(self.iLaserOff)
        
        
    def Get_Unique_Vals(self):
        # find uniqe vals and determine which motor was scanned
        # scanned motor has > 1 unique vals
    
        # determine the unique vals
        self.aUq_SCAN_ID = np.unique(self.aSCAN_ID)

        # get number of scan points from the unqie vals       
        self.nSCANpts = np.ptp(self.aSCAN_ID);
    
        # get number of scan points with XFEL on
        if self.nTotalDARKShots != 0:
            # scan point for darks needs to be removed
            self.nSCANptsXFEL = self.nSCANpts - 1
        else:
            self.nSCANptsXFEL = self.nSCANpts 
        
        # get shots per scan point ,need to take off darks though
        self.nShots_per_point = self.nTotalXFELShots/self.nSCANptsXFEL        
        
        # loop over motors and get unique vals
        for mtr in range(self.nMtrStrt,self.nCols):   
            arr_init = "self.aUq_"+"M"+str(mtr)+" = np.unique(self.aM"+str(mtr)+")"
            exec arr_init
            # determine scanned motor by number of uniqe vals
            uq_vals_str = "uq_val = np.unique(self.aM"+str(mtr)+")" 
            exec uq_vals_str
            # get number of uniqe vals
            if len(uq_val) > 1:
                self.nScannedMotorNum = mtr
                self.sScannedMotorName = self.Header[mtr]
    
    def Create_TagNumber_Array(self):
        # create an array for each scan id that has the tag numbers
        # allows easy indexing for comparing to tag numbers from
        # hdf 5 file
        
        # get dark tag numbers first
        self.aDarkTagNumbers = self.aTagnumber[self.iDark]
        
        # make 2 col array with SCAN ID and tagnumber for laser on
        self.aLaserOnTagNumbers = np.array([self.aTagnumber[self.iLaserOn],self.aSCAN_ID[self.iLaserOn]])
        #self.aSCAN_ID_LaserOn = self.aSCAN_ID[self.iLaserOn]
        
        # make 2 col array with SCAN ID and tagnumber for laser on                
        self.aLaserOffTagNumbers = np.array([self.aTagnumber[self.iLaserOff],self.aSCAN_ID[self.iLaserOff]])
        #self.aSCAN_ID_LaserOff = self.aSCAN_ID[self.iLaserOff]

    
    
    def Load_and_Calc_All(self):
        # perform all relevant operations on the file
        # to get indices etc
        
        # open the file        
        self.Open_CSV()
        
        # convert to arrays
        self.List_to_Array()
        
        # get unique vals and scanned motor
        self.Get_Unique_Vals()
     
        # get the dark,laser on/off indices
        self.Get_Dark_Laser_Indices()
                 
        # make the arrays with tag numbers for darks, laser on, laser off
        self.Create_TagNumber_Array()         
         
        