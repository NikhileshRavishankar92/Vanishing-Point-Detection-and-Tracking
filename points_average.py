import numpy as np

def vanishing_point(vanishing_points, img_width, img_height, filter_width, filter_height, threshold):
    L_row = img_height/filter_width 
    L_column = img_width/filter_height
    counter = np.zeros([L_row,L_column], dtype = int)
    
    j = 0
    l2 = 0
    while j < img_width:
        i = 0
        l1 = 0
        while i < img_height:
            for point in vanishing_points:
                    if (i < point[1] < i+filter_width) and (j < point[0] < j+filter_height):
                        counter[l1, l2] = counter[l1,l2] + 1
            i+=filter_width
            l1+=1  
        j+=filter_height
        l2+=1
    vanishing_points = np.array(vanishing_points)
    index = np.argmax(counter)
    index_row = index/L_column
    index_column = index - (index_row * L_column)
    k1 = []
    k2 = [] 
    ul_1 = (index_column * filter_height + threshold)
    ll_1 = (index_column * filter_height - threshold)
    ul_2 = (index_row * filter_height + threshold)
    ll_2 = (index_row* filter_height - threshold)   
    k1 = vanishing_points[:,0][vanishing_points[:,0] < ul_1]
    k1 = k1[k1 > ll_1 ]
    k2 = vanishing_points[:,1][vanishing_points[:,1] < ul_2 ]
    k2 = k2[k2 > ll_2]
    return (np.mean(k1),np.mean(k2))
    
#points = np.load('Vanishing_point_locations.npy')


    

