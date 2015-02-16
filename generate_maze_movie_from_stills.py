# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 10:44:04 2015

Make a Image from sub images and convert to video....

@author: Luke Boorman
"""

import cv2
import os
#import re
import numpy as np

# Location of img files and for movie output....
main_img_dir='D:/robotology/hclearn/division_street_1/maze_path'

# map imges
map_img_prefix='map_img_'
# maze images
maze_img_prefix='maze_img_'
# dict images
dict_img_prefix='dict_img_'

## Turn on/off here to show the frames as they are generated... faster movie encoding if off
show_output_frames=True

## Maximum number of frames to show....
max_step_frames=500

### Frame rate of generated movie 
frame_rate=30 #FPS
#### Movie type

## 1. 1st person Step movie -> shows images viewed, map, dictionaries
make_step_movie=False
# Output
video_fname='First_person_movie.avi'

## 2. Compare learning -> just shows maps
make_map_movie=True
cascade_timing_of_images=True # This shows each image set in sequence....
# Output
map_video_fname='map_output_compare_path.avi'
## Make list of directories where maps are.... maps will be order from left to right in movie...
map_directory_list = []
title_list = []
map_directory_list.append("D:/robotology/hclearn/division_street_1/maze_path") # Random path
title_list.append("Random path")
map_directory_list.append("D:/robotology/hclearn/division_street_1/active_learn_cur/maze_path") # Curiosity only path
title_list.append("Curiosity only")
map_directory_list.append("D:/robotology/hclearn/division_street_1/active_learn_cur_mmtm/maze_path") # Curiosity + momentum
title_list.append("Curiosity & Momentum")


if make_step_movie:
    # database of files
    map_file_database=np.empty(0,dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')])
    maze_file_database=np.empty(0,dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')])
    dict_file_database=np.empty(0,dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')])
            
    map_image_count=0
    maze_image_count=0
    dict_image_count=0
    if os.path.exists(main_img_dir):
        for file in os.listdir(main_img_dir):
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
    
    # Cut down to number of frames if needed....    
    if len(maze_file_database)>max_step_frames:
        maze_file_database=maze_file_database[:max_step_frames]    
        map_file_database=map_file_database[:max_step_frames]
        dict_file_database=dict_file_database[:max_step_frames]
    #### Load and combine images, as vertical stack with map centred below.....
    # Load first image to get sizes
    map_image=cv2.imread(os.path.join(main_img_dir,map_file_database['img_fname'][0]))                
    maze_image=cv2.imread(os.path.join(main_img_dir,maze_file_database['img_fname'][0]))                
    dict_image=cv2.imread(os.path.join(main_img_dir,dict_file_database['img_fname'][0])) 
    
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
    out = cv2.VideoWriter(os.path.join(main_img_dir,video_fname),fourcc, float(frame_rate), (video_out_w,video_out_h)) # -1 fourcc
    
    if out==None:
        print 'Writer error = none'
    if out==False:     
        print 'Writer false'
    
    print out
    
    for current_file in range(0,len(map_file_database)):
        map_image=cv2.imread(os.path.join(main_img_dir,map_file_database['img_fname'][current_file]))                
        maze_image=cv2.imread(os.path.join(main_img_dir,maze_file_database['img_fname'][current_file])) 
        dict_image=cv2.imread(os.path.join(main_img_dir,dict_file_database['img_fname'][current_file]))     
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
    print 'Movie generated....'
    
if make_map_movie:
    # Load in map images.....
    map_file_database=[]
    for current_dir in range(0,len(map_directory_list)):
        map_file_database.append(np.empty(0,dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')]))
        map_image_count=0
        if os.path.exists(map_directory_list[current_dir]):
            for file in os.listdir(map_directory_list[current_dir]):
                if file[0:len(file)-9]==map_img_prefix:
                    file_ttt=np.empty(1, dtype=[('orig_file_id','i2'),('file_id','i2'),('img_txt','a100'),('img_fname','a100')])
                    file_ttt['orig_file_id'][0]=int(file[len(file)-9:len(file)-4])
                    file_ttt['img_fname'][0]=file
                    file_ttt['img_txt'][0]=file[0:len(file)-9] 
                    file_ttt['file_id'][0]=map_image_count
                    map_file_database[current_dir] = np.append(map_file_database[current_dir],file_ttt,axis=0)
                    map_image_count += 1
            map_file_database[current_dir]=np.sort(map_file_database[current_dir],order=['orig_file_id'])
                # Cut down to number of frames if needed....    
            if len(map_file_database[current_dir])>max_step_frames:  
                map_file_database[current_dir]=map_file_database[current_dir][:max_step_frames]
    
    map_image=cv2.imread(os.path.join(map_directory_list[0],map_file_database[0]['img_fname'][0]))                
    h1, w1 = map_image.shape[:2]
    # video
    # Size.....
    video_h=h1
    video_w=w1*len(map_directory_list)
    video_d=3 # no colour channels
    ## Video out must be divisible by 2
    video_out_h=np.round(video_h/2)*2
    video_out_w=np.round(video_w/2)*2
    cap = cv2.VideoCapture(0)
    # Define the codec and create VideoWriter object
    fourcc = cv2.cv.CV_FOURCC('X', 'V', 'I', 'D')# cv2.VideoWriter_fourcc(*'XVID')
    #fourcc = cv2.cv.CV_FOURCC('x', '2', '6', '4')# cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(os.path.join(main_img_dir,map_video_fname),fourcc, float(frame_rate), (video_out_w,video_out_h)) # -1 fourcc
    
    if out==None:
        print 'Writer error = none'
    if out==False:     
        print 'Writer false'
    
    print out
    
    # Show images as ordered sequence
    if cascade_timing_of_images:
        
        # Step through each set of images......
        start_blend = np.zeros((video_h, video_w,video_d), np.uint8)#np.zeros((h1, w1,video_d,len(map_file_database)), np.uint8)
        end_blend = np.zeros((video_h, video_w,video_d), np.uint8)#np.zeros((h1, w1,video_d,len(map_file_database)), np.uint8)
        blank_image=np.zeros((h1, w1,video_d), np.uint8)
        ### Get start and finish images and blend....        
        for current_dir in range(0,len(map_file_database)):
            # Start image
            map_image=cv2.imread(os.path.join(map_directory_list[current_dir],map_file_database[current_dir]['img_fname'][0]))
            textsize=cv2.getTextSize(title_list[current_dir],cv2.FONT_HERSHEY_SIMPLEX,0.8,2)
            cv2.putText(map_image, title_list[current_dir], ((w1/3)+(textsize[0][1]/2),\
                h1-int(textsize[1]/2)-20), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0,255,0),2); 
            start_blend[:h1, w1*(current_dir):w1*(current_dir+1),:video_d]=cv2.addWeighted(map_image,0.5,blank_image,0.5,0)#map_image           
            map_image=cv2.imread(os.path.join(map_directory_list[current_dir],map_file_database[current_dir]['img_fname'][-1]))
            cv2.putText(map_image, title_list[current_dir], ((w1/3)+(textsize[0][1]/2),\
                h1-int(textsize[1]/2)-20), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0,255,0),2);            
            end_blend[:h1, w1*(current_dir):w1*(current_dir+1),:video_d]=cv2.addWeighted(map_image,0.5,blank_image,0.5,0)#map_image                  
        
        # use start images for initial
        base_image=start_blend
        for current_dir in range(0,len(map_file_database)):
 #           vis = np.zeros((video_h, video_w,video_d), np.uint8)
            for current_file in range(0,len(map_file_database[current_dir])):
                #for current_image_set in range(0,len(map_file_database)):
                vis = base_image #np.zeros((video_h, video_w,video_d), np.uint8)
                map_image=cv2.imread(os.path.join(map_directory_list[current_dir],map_file_database[current_dir]['img_fname'][current_file]))                    
                # Add text            
                textsize=cv2.getTextSize(title_list[current_dir],cv2.FONT_HERSHEY_SIMPLEX,0.8,2)
                cv2.putText(map_image, title_list[current_dir], ((w1/3)+(textsize[0][1]/2),\
                    h1-int(textsize[1]/2)-20), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0,255,0),2);            
                ## Luke maze imge on top and dict + map below....
                # Insert maze image
                textsize=cv2.getTextSize("step:"+str(current_file),cv2.FONT_HERSHEY_SIMPLEX,0.8,2)
                cv2.putText(map_image, "step:"+str(current_file), (30+(textsize[0][1]/2),\
                    30+int(textsize[1]/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0,255,0),2);  
                vis[:h1, w1*(current_dir):w1*(current_dir+1),:video_d] = map_image
                vis =cv2.resize(vis, (video_out_w, video_out_h))       
                out.write(vis)
            
                if show_output_frames:
                    cv2.imshow("test", vis)
                    cv2.waitKey(50)
            # Overwrite start images once completed
            base_image[:h1, w1*(current_dir):w1*(current_dir+1),:video_d]=end_blend[:h1, w1*(current_dir):w1*(current_dir+1),:video_d]
                
    else:    # Show images althoughter
        for current_file in range(0,len(map_file_database[0])):
            vis = np.zeros((video_h, video_w,video_d), np.uint8)
            for current_dir in range(0,len(map_file_database)):
                map_image=cv2.imread(os.path.join(map_directory_list[current_dir],map_file_database[current_dir]['img_fname'][current_file]))                    
                # Add text            
                textsize=cv2.getTextSize(title_list[current_dir],cv2.FONT_HERSHEY_SIMPLEX,0.8,2)
                cv2.putText(map_image, title_list[current_dir], ((w1/3)+(textsize[0][1]/2),\
                    h1-int(textsize[1]/2)-20), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0,255,0),2);            
                ## Luke maze imge on top and dict + map below....
                # Insert maze image
                vis[:h1, w1*(current_dir):w1*(current_dir+1),:video_d] = map_image
            vis =cv2.resize(vis, (video_out_w, video_out_h))
            textsize=cv2.getTextSize("step:"+str(current_file),cv2.FONT_HERSHEY_SIMPLEX,0.8,2)
            cv2.putText(vis, "step:"+str(current_file), (30+(textsize[0][1]/2),\
                30+int(textsize[1]/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0,255,0),2);        
            out.write(vis)
            
            if show_output_frames:
                cv2.imshow("test", vis)
                cv2.waitKey(50)       
            
    # Release everything if job is finished
    #cv2.waitKey(500)
    cap.release()
    out.release()
    cv2.destroyAllWindows() 
    print 'Movie generated....'