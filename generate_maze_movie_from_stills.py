# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 10:44:04 2015

Make a Image from sub images and convert to video....


@author: luke
"""

import cv2
import glob
import os
#import re
import numpy as np

img_dir='D:/robotology/hclearn/division_street_1/maze_path'
# Output
video_fname='output.avi'
# map imges
map_img_prefix='map_img_'
# maze images
maze_img_prefix='maze_img_'
# dict images
dict_img_prefix='dict_img_'

show_output_frames=False


#no_files=len(glob.glob(os.path.join(img_dir, '*.jpg')))
# database of files
map_file_database=np.empty(0,dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')])
maze_file_database=np.empty(0,dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')])
dict_file_database=np.empty(0,dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')])
        
map_image_count=0
maze_image_count=0
dict_image_count=0
if os.path.exists(img_dir):
    for file in os.listdir(img_dir):
        #parts = re.split("[-,\.]", file)         
        if file[0:len(file)-9]==map_img_prefix:
            file_ttt=np.empty(1, dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')])
            file_ttt['orig_file_id'][0]=int(file[len(file)-9:len(file)-4])
            file_ttt['img_fname'][0]=file
            file_ttt['img_txt'][0]=file[0:len(file)-9] 
            file_ttt['file_id'][0]=map_image_count
            map_file_database = np.append(map_file_database,file_ttt,axis=0)
            map_image_count += 1 
        elif file[0:len(file)-9]==maze_img_prefix:
            file_ttt=np.empty(1, dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')])
            file_ttt['orig_file_id'][0]=int(file[len(file)-9:len(file)-4])
            file_ttt['img_fname'][0]=file  
            file_ttt['img_txt'][0]=file[0:len(file)-9] 
            file_ttt['file_id'][0]=maze_image_count
            maze_file_database = np.append(maze_file_database,file_ttt,axis=0)
            maze_image_count += 1
        elif file[0:len(file)-9]==dict_img_prefix:
            file_ttt=np.empty(1, dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')])
            file_ttt['orig_file_id'][0]=int(file[len(file)-9:len(file)-4])
            file_ttt['img_fname'][0]=file  
            file_ttt['img_txt'][0]=file[0:len(file)-9] 
            file_ttt['file_id'][0]=dict_image_count
            dict_file_database = np.append(dict_file_database,file_ttt,axis=0)
            dict_image_count += 1 
else:
    raise NameError("Folder does not exists")  

# Sort datbases by orig_file_id
maze_file_database=np.sort(maze_file_database,order=['orig_file_id'])
map_file_database=np.sort(map_file_database,order=['orig_file_id'])
dict_file_database=np.sort(dict_file_database,order=['orig_file_id'])
#### Load and combine images, as vertical stack with map centred below.....
# Load first image to get sizes
map_image=cv2.imread(os.path.join(img_dir,map_file_database['img_fname'][0]))                
maze_image=cv2.imread(os.path.join(img_dir,maze_file_database['img_fname'][0]))                
dict_image=cv2.imread(os.path.join(img_dir,dict_file_database['img_fname'][0])) 

h1, w1 = maze_image.shape[:2]
h2, w2 = map_image.shape[:2]
h3, w3 = dict_image.shape[:2]

w1_offset=np.round(w1/2)
w2_offset=np.round(w2/2)
w3_offset=np.round(w3/2)
# video
# Size.....

video_h=h1+h2
video_w=max(w1,w2+w3)
video_d=3 # no colour channels
## Video out must be divisible by 2
video_out_h=np.round(video_h/2)*2
video_out_w=np.round(video_w/2)*2


cap = cv2.VideoCapture(0)
# Define the codec and create VideoWriter object
fourcc = cv2.cv.CV_FOURCC('X', 'V', 'I', 'D')# cv2.VideoWriter_fourcc(*'XVID')
#fourcc = cv2.cv.CV_FOURCC('x', '2', '6', '4')# cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(os.path.join(img_dir,video_fname),fourcc, 10.0, (video_out_w,video_out_h)) # -1 fourcc

if out==None:
    print 'Writer error = none'
if out==False:     
    print 'Writer false'

print out

for current_file in range(0,len(map_file_database)):
    map_image=cv2.imread(os.path.join(img_dir,map_file_database['img_fname'][current_file]))                
    maze_image=cv2.imread(os.path.join(img_dir,maze_file_database['img_fname'][current_file])) 
    dict_image=cv2.imread(os.path.join(img_dir,dict_file_database['img_fname'][current_file]))     
    vis = np.zeros((video_h, video_w,video_d), np.uint8)
    
    ## Luke maze imge on top and dict + map below....
    # Insert maze image
    vis[:h1, :w1,:video_d] = maze_image
    # Insert map image
    vis[h1:h1+h3, :w2,:video_d] = map_image
    # insert dict image
    vis[h1:h1+h3, video_w-w3:video_w,:video_d] = dict_image
    
    
#    vis[h1:h1+h2, w1_offset-w2_offset:(w1_offset-w2_offset)+w2,:video_d] = map_image
    # Write frame to video
    #ttt=np.array((video_h, video_w,video_d), np.uint32)
    vis =cv2.resize(vis, (video_out_w, video_out_h))
    #ttt=vis#np.array(vis, np.int32)
    #ttt *=(256*256)
    #cv2.cvtColor(vis,ttt,cv2.CV_32SC3)
    # out.write(vis)
    out.write(vis)
    
    if show_output_frames:
        cv2.imshow("test", vis)
        cv2.waitKey(50)
# Release everything if job is finished
#cv2.waitKey(500)
cap.release()
out.release()
cv2.destroyAllWindows()


print 'End'