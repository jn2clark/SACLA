# SACLA
CSV and HDF reader for SACLA XFEL data.  The CSV reader takes the CSV that is output from the DAQ and sorts the tagnumbers into darks, laser on and off.  The corresponding tag numbers are then used to sort the hdf files (which only contain tag numbers and images).  Use ReadSaclaHDF to read in both CSV and sort the HDF.
