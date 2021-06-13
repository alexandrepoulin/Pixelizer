from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import colorsys as cs

###################################
## Script parameters
###################################

#path to file
image_filename = "sunset.jpeg"
output_filename = "sunset_pixelized.png" 
output_type = "png"

n_colors = 5

#how many colors to add to the pallet for each main color.
extend_brighter = 2 #adds this number of brighter shades
extend_darker = 2 #adds this number of darker shades

#How big of a square in pixels to compress to a single pixel
#if this is not a multiple of the size, then the image will be
#cut off at the bottom and right.
compression_factor = 4

#whether to simply replace the color, or create a smaller image
same_size = True

##multipliers for shade
##For making something brighter: new_c = h, s/c_sat, v * c_val
##For making something darker: new_c = h*c_hue, s*c_sat, v / c_val
c_hue = 1.1 ##used for darkening only
c_sat = 1.2 
c_val = 1.2

#pallet mods
#changes to the centroid colors for the pallet
e_sat = 1.2
e_val = 1.0

#change the average of the square to find the paller
i_sat = 1.2
i_val = 1.2


###################################
## Script brains
###################################
##funtion to get the main colors of an image 
def getMainColors(flat_data,num_clusters):
    kmeans = KMeans(init="k-means++", n_clusters=num_clusters, n_init=3)
    kmeans.fit(flat_data)
    return kmeans.cluster_centers_ ##RGB values

##image file processing    
def getImageData(filename):
    """Get the file data"""
    with Image.open(filename,'r') as fin:
        return np.asarray(fin)

def flatten(x):
    data= []
    for y in x:
        data.extend(y)
    return np.array(data)

def extendColor(c, num_brighter, num_darker):
    #expect HSV value
    h, s, v= cs.rgb_to_hsv(*(x/255 for x in c))
    s = min(1,max(0,s*e_sat))
    v = min(1,max(0,v*e_val))
    colors = []
    ##For making something brighter: new_c = h, s/c_sat, v * c_val
    ##For making something darker: new_c = h*c_hue, s*c_sat, v / c_val
    for i in range(num_brighter, -num_darker-1, -1):
        new_c =[] 
        if i>=0:
            new_c = (h,min(1, max(0,s/pow(c_sat,i))), min(1,max(0,v*pow(c_val,i))) )
        else:
            new_h = (np.sign(np.cos(((h-1/6)%1)* np.pi))*c_hue + h)%1
            new_c = (new_h,min(1, max(0,s*pow(c_sat,i))), min(1,max(0,v/pow(c_val,i))) )
        colors.append([x*255 for x in cs.hsv_to_rgb(*new_c)])
    return colors
    

def findPalletColor(c, pallet):
    bestScore = 1000000000
    best_c = None
    for col in pallet:
        score= np.linalg.norm(c-col)
        if score< bestScore:
            bestScore = score
            best_c = col
    return best_c 

##Use the pallet to create a new image. 
#c i the compression factor, just saving on typing.
#ss is same_size
def createNewImage(data, pallet, c, ss):
    new_data = data
    if not ss:
        new_data = np.zeros((len(data)//c,len(data[0])//c))

    csq = c*c

    for row in range(0,len(data),c):
        for col in range(0, len(data[0]),c):
            r = data[row:row+c,col:col+c,0].flatten()
            g = data[row:row+c,col:col+c,1].flatten()
            b = data[row:row+c,col:col+c,2].flatten()
            r = [int(x)*int(x) for x in r]
            g = [int(x)*int(x) for x in g]
            b = [int(x)*int(x) for x in b]
            r = np.sqrt(sum(r)/csq)/255
            g = np.sqrt(sum(g)/csq)/255
            b = np.sqrt(sum(b)/csq)/255
            h,s,v = cs.rgb_to_hsv(r,g,b)
            r,g,b = (round(255*x) for x in cs.hsv_to_rgb(h,s*i_sat, v*i_val))
            
            chosen_c = findPalletColor(np.array([r,g,b]), pallet)
            if ss:
                for i in range(c):
                    for j in range(c):
                        new_data[row+i][col+j] = chosen_c
            else:
                new_data[row//c][col//c] = chosen_c
    return new_data







#step 1: Get image data
data = getImageData(image_filename)
height_cutoff = len(data) - (len(data)%compression_factor)
width_cutoff = len(data[0]) - (len(data[0])%compression_factor)
data = np.array([x[:width_cutoff] for x in data[:height_cutoff]])
flat_data = flatten(data)

#step 2: Get the centroids
centroids = getMainColors(flat_data,n_colors)

#step 3: Extend main colors include brighter and darker versions
pallet = []
for c in centroids:
    #c is an rgb with vals between 0 and 1
    print("centroid: ", c)
    pallet.extend(extendColor(c,extend_brighter,extend_darker))
##the pallet is now all in RGB
for c in pallet:
    print(c)

#step 4: create a new image using out pallet
new_data = createNewImage(data,pallet, compression_factor, same_size)
im = Image.fromarray(new_data)
im.save(output_filename, output_type)


