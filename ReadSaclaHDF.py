# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 15:20:40 2015

@author: jesseclark

Reads in the MPCCD images from SACLA hdf files
Sorts based on the tag numbers in the csv output from
the DAQ according to the scan var (delay time) and shutter
status (XFEL and optical).  

"""
import h5py
import ReadSaclaCSV
import numpy as np

# read the hdf
class BinEvents:
    
    def __init__(self, run_number):
        
        # change these dirs and filenames 
        # where to look for data and csv files
        self.sHDF_dir = "~/Documents/SACLA-June-H20/scan_input/"
        self.sCSV_dir = "~/Documents/SACLA-June-H20/scan_input/"
        
        self.sCSV_filename = self.sCSV_dir+"run"+str(run_number)+"_out.csv"
        self.sHDF_filename = self.sHDF_dir+str(run_number)+".h5"
        
        # read in csv file and get tag numbers
        self.CSV_file = ReadSaclaCSV.SACLA_CSV(self.sCSV_filename)
        
        # load and calc all indices from CSV file
        self.CSV_file.Load_and_Calc_All()
        
        # read in hdf
        self.fh5 = h5py.File(self.sHDF_filename,'r')
        
        # get path to the detector
        self.run_n = str(self.fh5.keys()[1])
        
        self.det_local = str(self.fh5[self.fh5.keys()[1]].keys()[0])
        
        # creat path to images
        self.imgs_path = '/'+self.run_n+'/'+self.det_local
        
        # get image tags
        self.exposure_tags = self.fh5[self.imgs_path].keys()[1:]
        
        # det path
        self.det_path = str(self.fh5[self.imgs_path +'/' + self.exposure_tags[0]].keys()[0])

        #
        #self.Get_Dark_Images()
        
    def Get_Dark_Images(self, Return_mean = False):
        
        # get the dark images from the hdf
        self.counter = 0
        # use dark tag numbers to get the dark image
        if self.CSV_file.nTotalDARKShots > 0:
            for tag_n in self.CSV_file.aDarkTagNumbers:
                # init the array on first pass
                if self.counter == 0:
                    self.aDarkImg = self.fh5[self.imgs_path + '/tag_' + str(tag_n) +'/'+ self.det_path].value    
                else:
                    # add to the array
                    self.aDarkImg += self.fh5[self.imgs_path + '/tag_' + str(tag_n) +'/'+ self.det_path].value    
                self.counter += 1
            if Return_mean:
                # return the average in case diff numbs of dark to laser on/off
                self.aDarkImg /= self.counter
                print 'Returning mean of dark images'
            else:
                print 'Returning sum of dark images'
    
    def Get_LaserOn_Images(self, Return_mean = False):
        # get the laser on images
    
        # read the first laser on image size
        self.aImgSize = self.fh5[self.imgs_path + '/tag_' + str(self.CSV_file.aLaserOnTagNumbers[0,0]) +'/'+ self.det_path].shape    
    
        # init the array
        self.aLaserOnImg = np.zeros([self.aImgSize[0],self.aImgSize[1],self.CSV_file.nSCANptsXFEL])        
        
        # init array of bin counts for averaging        
        self.aLaserOnBinCounts = np.zeros(self.CSV_file.nSCANptsXFEL)
        
        # now loop through laser on image tags
        for shot_n in range(0,self.CSV_file.nTotalXFEL_Laser_on):
                        
            # get the tag and scan id 
            tag_shot = self.CSV_file.aLaserOnTagNumbers[:,shot_n]
            
            # now fill the data cube and index by scan id 
            # scan id starts at 1 so subtract 1 to index from 0
            self.aLaserOnImg[:,:,tag_shot[1]-1] += self.fh5[self.imgs_path + '/tag_' + str(tag_shot[0]) +'/'+ self.det_path].value    
            self.aLaserOnBinCounts[tag_shot[1]-1] += 1
        
        if Return_mean:
            # now loop and average, could vectorize but will save memory with loop
            for arr_ind in range(0,self.aLaserOnImg.shape[2]):
                self.aLaserOnImg[:,:,arr_ind] /= self.aLaserOnBinCounts[arr_ind]
            
            print 'Returning mean of Laser On images'

        else:
            
            print 'Returning sum of Laser On images'
            
    def Get_LaserOff_Images(self, Return_mean = False):
        # get the laser on images
    
        # read the first laser off image size
        self.aImgSize = self.fh5[self.imgs_path + '/tag_' + str(self.CSV_file.aLaserOffTagNumbers[0,0]) +'/'+ self.det_path].shape    
    
        # init the array
        self.aLaserOffImg = np.zeros([self.aImgSize[0],self.aImgSize[1],self.CSV_file.nSCANptsXFEL])        
        
        # init array of bin counts for averaging        
        self.aLaserOffBinCounts = np.zeros(self.CSV_file.nSCANptsXFEL)
        
        # now loop through laser off image tags
        for shot_n in range(0,self.CSV_file.nTotalXFEL_Laser_off):
                        
            # get the tag and scan id 
            tag_shot = self.CSV_file.aLaserOffTagNumbers[:,shot_n]
            
            # now fill the data cube and index by scan id 
            # scan id starts at 1 so subtract 1 to index from 0
            self.aLaserOffImg[:,:,tag_shot[1]-1] += self.fh5[self.imgs_path + '/tag_' + str(tag_shot[0]) +'/'+ self.det_path].value    
            self.aLaserOffBinCounts[tag_shot[1]-1] += 1
            
        if Return_mean:    
            # now loop and average, could vectorize but will save memory with loop
            for arr_ind in range(0,self.aLaserOffImg.shape[2]):
                self.aLaserOffImg[:,:,arr_ind] /= self.aLaserOffBinCounts[arr_ind]
            
            print 'Returning mean of Laser Off images'

        else:
            
            print 'Returning sum of Laser Off images'