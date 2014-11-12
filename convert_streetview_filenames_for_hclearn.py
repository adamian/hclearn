# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 10:22:52 2014

Process maze images for HClearn code....

1. Cant have negative grid locations...
2. Cant have additional '-' 

Code
1. Shifts all image grid locations to positive
2. Removes long and lat descriptors


@author: luke
"""
import numpy as np
#import sys
import os
import glob

# Path to images # REMEMBER FORWARD SLASHES
pathname = 'D:/robotology/hclearn/division_street_1'
heading_index='NESW' #N=0, E=1, S=2, W=3

no_files=len(glob.glob(os.path.join(pathname, '*.jpg')))

#file_database=np.empty([5,no_files],dtype=int)
file_database=np.empty(no_files,\
    dtype=[('file_id','i2'),('x_loc','i2'),('y_loc','i2'),('heading','i2'),('img_id','i2')])
#,no_files],dtype=int)
file_database['file_id'][:]=range(0,no_files)
piclist = []
image_count=0
IMG_SUFFIX = ".jpg"  

for infile in glob.glob(os.path.join(pathname, '*.jpg')):
    # ADD filename to list    
    piclist.append(infile)
    # Extract relevant file information.....
    # find start of filename section
    file_info=piclist[image_count][piclist[image_count].find("\\")+1:piclist[image_count].find("\\")+14]
    # img count , x, y, heading, img_num    
    # x grid
    file_database['x_loc'][image_count]=int(file_info[0:3])
    # y grid    
    file_database['y_loc'][image_count]=int(file_info[4:7])
    # Convert letter heading to index 1= N, 2=E, 3=S, 4=W
    file_database['heading'][image_count]=heading_index.find(file_info[8:9])
    # File identifier (optional extra e.g. two files at same location x,y and direction)
    file_database['img_id'][image_count]=int(file_info[10:13])
    # Massive data image block!!!
    #img_file[image_count,:,:,:]=cv2.imread(infile)
    image_count += 1

# Find minimum x value
x_min=file_database['x_loc'].min()
y_min=file_database['y_loc'].min()

print('Files will be adjsuted with x +',str(-x_min),' and y +', str(-y_min))

###### Rename each file with x,y offset and no lon/lat
for infile in range(0,len(piclist)):
    new_fn = os.path.join(pathname, str(file_database['x_loc'][infile]-x_min).zfill(3) + "-" + str(file_database['y_loc'][infile]-y_min).zfill(3) + "-" + heading_index[file_database['heading'][infile]]+ "-" + str(file_database['img_id'][infile]).zfill(3) + IMG_SUFFIX)  
    os.rename(piclist[infile],new_fn)



          





