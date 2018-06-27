# -*- coding: utf-8 -*-
"""
Created on Thu May 31 09:52:28 2018

@author: D.C Woszczyk

This file contains classes used to prepare shapefiles for computation
 by precalculating some one time actions

- joins shapefiles
- compute density centers of neighbourhoods
- count number of neighbours for houses
"""

import geopandas as gpd
from sklearn.neighbors import KDTree
import pandas as pd
import time


#compute the density centre of a neighbourhood
# using building density 
def getDensityCenter(data,buurt):
    x=0
    y=0
    
    for i in range(len(data)):
        x+= data.iloc[i].geometry.centroid.x
        y+=data.iloc[i].geometry.centroid.y
    
    centx= x/len(data)
    centy = y/len(data)
    
    #center= Point(centx,centy)
    

    return centx,centy
        
    
   
#get element within a distance of a centre of a neighbourhood    
def getWithinDist(data,buurt,distance):
    
    houses= data[["geometry"]]
    
    buurt= buurt[['geometry']]
    
    houses.append(buurt)
    
    #get houses id  within 200m
    filthouses = getIdAround(houses,distance)
    filthouses=  filthouses[len(filthouses)-1]
    
    cols = ['gid',]
    lst = []
    
    gid= pd.DataFrame(columns=['gid'])
    
    for i in range(len(filthouses)):
        #print("ind[x] ", ind[x])
        #print("i ",i)
        #print(dist[len(data)-1][i])
        gid= data.iloc[i]["gid"]
        
        lst.append([gid])
        
       
    ids = pd.DataFrame(lst, columns=cols)  
    
    res= data.loc[(data["gid"].isin(ids["gid"]))]
    
    #count total surface of buildings
      #totsurf=getSurface(alldata)
      
    print("houses collected")
    return res
    

#count the number of adjacent elements
#used for neighbourhood and houses
def countNeighbours(df):
    df["neighbors"] = None  # add NEIGHBORS column

    print("number of houses", len(df))
    for index, country in df.iterrows():  
        # get 'not disjoint' countries
        neighbors = df[~df.geometry.disjoint(country.geometry)].gid.tolist()
        # remove own name from the list
        neighbors = [ gid for gid in neighbors if country.gid != gid ]
        # add names of neighbors as NEIGHBORS value
        #df.at[index, "neighbors"] = ", ".join(neighbors)
        df.at[index, "neighbors"] = len(neighbors)
        #print("neighbour", neighbors)

    return df

#get the x an y of the centre of a neighbourhood
def getcoord(data):
    #print(data.head())
    x = data.geometry.centroid.x
    y = data.geometry.centroid.y
    return x,y

#get the id's of elements withing distance
def getIdAround(data,distance):
    print("getting the IDs around 200m")
    
    data= gpd.GeoDataFrame(data)
    #print(data.head())
    
    print("total data points before 200m filter ", len(data))
    data['x'],data['y']= getcoord(data)
    
    treedt= data[['x','y']]
    buildTree = KDTree(treedt)
    
    point =data[['x','y']]

    res = buildTree.query_radius(point,r=distance)
    
    return res

#filter neigbhours
def selectNeighbours(data,distance):
    dat= data
    
    res= getIdAround(data,distance)
    #get minimal distance to each polygons
    #select neighbourhoods that are within 300m
    
    filt=[]
    
    for i in range(len(res)):
        ar=[]
        for j in range(len(res[i])):
          #  print("i ",i)
           # print("data index ",res[i][j])
            center = data.iloc[i].geometry.centroid
            
            polygon = dat.iloc[res[i][j]].geometry
            
            #print("polygon:", polygon)
            
            if(center.distance(polygon)<=300):
               ar.append(res[i][j]) 
               
        filt.append(ar)

    #print("count results ",res )
    return filt

#merge two files
def fileglue(file1,file2):
       glued= gpd.sjoin(file1, file2,how="inner", op='intersects') 
       return glued


#select neighbourhood from the list 
def filterDown(dtb,ind,data,x):
    
    cols = ['BU_NAAM','GM_NAAM']
    lst = []
    
    names= pd.DataFrame(columns=['BU_NAAM','GM_NAAM'])

   # print("Is index right? Name: ",dtb.iloc[x]["BU_NAAM"])
    #print("ind ", ind)
    
    for i in ind[x]:
        #print("ind[x] ", ind[x])
        #print("i ",i)
        #print(dist[len(data)-1][i])
        name1= dtb.iloc[i]["BU_NAAM"]
        name2= dtb.iloc[i]["GM_NAAM"]
        
        lst.append([name1,name2])
        
   
    names = pd.DataFrame(lst, columns=cols)  
    
    #print("names ",names)
      
    res= data.loc[(data["BU_NAAM"].isin(names["BU_NAAM"])) & (data["GM_NAAM"].isin(names["GM_NAAM"]))]
    
    return res


#
def main(dt,dt2,buurts):
    
    dt=dt[dt['BU_NAAM'] != "Verspreide huizen"]
    neigh= dt[["BU_NAAM",'GM_NAAM']]
    neigh=neigh.drop_duplicates()

    
    #select the neighbourhoods present 
    bu=buurts.loc[(buurts["BU_NAAM"].isin(neigh["BU_NAAM"])) & (buurts["GM_NAAM"].isin(neigh["GM_NAAM"]))]
    bu = bu.reset_index()
    
    print("lit of neigh after filter  ", len(bu))
    
    bu=gpd.GeoDataFrame(bu)

    
    #compute neighbourhoods within 5000 m
    
    ind=selectNeighbours(bu,5000)
    
    print("ind length ", len(ind))


    bu=pd.DataFrame(bu)
    bu=bu[["BU_NAAM","GM_NAAM"]]
    
    #add centroid column
    bu['centroid']= None

    #houses
    dtfo=dt2[dt2["gebruiksdo"] == "woonfunctie"]   
    dup= dtfo[["gid"]].drop_duplicates()
    dtfo=dtfo.loc[dtfo["gid"].isin(dup["gid"])]
    
    #all
    dup= dt[["gid"]].drop_duplicates()
    
    data = dt.iloc[0:0]
    
    
    for x in range(len(neigh)):
        print("---------------------------------------")
        print(neigh.iloc[x,:]['BU_NAAM']," ",neigh.iloc[x,:]['GM_NAAM'])
        print(x,"out of ",len(neigh))
        print("--------------------------------------- ")
        
            
        ##get index
        idx = bu.index[(bu['BU_NAAM'] == neigh.iloc[x,:]['BU_NAAM']) & (bu['GM_NAAM'] == neigh.iloc[x,:]['GM_NAAM'])].tolist()

        print("index ",idx)
        
        #select houses in the neigh
        burgHouses=dt[(dt['BU_NAAM'] == neigh.iloc[x,:]['BU_NAAM']) & (dt['GM_NAAM'] == neigh.iloc[x,:]['GM_NAAM']) ] 
       
        #get centroid an adds it to the buurt file
        centerx,centery= getDensityCenter(burgHouses,bu,idx)
        
        bu.at[idx, "centroid"]= list(zip(centerx, centery))
        
    bu = gpd.GeoDataFrame(bu, geometry='centroid')
    
    print(bu.head())
    
    
    
    for i in range(len(neigh)): 
        print("---------------------------------------")
        print(neigh.iloc[x,:]['BU_NAAM']," ",neigh.iloc[x,:]['GM_NAAM'])
        print(x,"out of ",len(neigh))
        print("--------------------------------------- ")
    
        #filter houses 300 m around the centroid
        dtd = getWithinDist(dtfo,bu,300)
        
        #get neighbours for houses around 300m
        neighbours= countNeighbours(dtd) 
        
        data=gpd.GeoDataFrame(pd.concat([data,neighbours]))

    
    return data,bu
    
    


#--------------------------------------------#
start_time = time.time()


##new buildins age + neihj
nage= "data/limburgage.shp"


##buurt shapes
b= "data/buurtlim2.shp"

##addresses data
point = "data/limburgfunctions.shp"
 

# Read data
#age = gpd.read_file(fp)

buurt = gpd.read_file(b)

#newage = gpd.read_file(nage)


points= gpd.read_file(point)
 
'''
f = pd.read_csv('centroids2.csv')

geometry = [Point(xy) for xy in zip(f.x, f.y)]
crs = {'init': 'epsg:28992'} #http://www.spatialreference.org/ref/epsg/2263/
geo_df = gpd.GeoDataFrame(f, crs=crs, geometry=geometry)

geo_df.to_file(driver='ESRI Shapefile', filename='neighbours.shp')

'''

#dt= fileglue(newage[["gid","bouwjaar","geometry"]],buurt[["BU_NAAM","GM_NAAM","geometry"]])


dt.to_file(driver = 'ESRI Shapefile', filename= "glue1.shp")


dt= gpd.read_file("2glue.shp")

file1 =dt[["gid","bouwjaar","BU_NAAM","GM_NAAM","geometry"]] 
file2 = points[["gebruiksdo","geometry"]] 


dt= fileglue(file1,file2)
print("second glue done")

dt2= fileglue(file1,file2)

#dt2.to_file(driver = 'ESRI Shapefile', filename= "glue2.shp")

#If done in two part, uncomments below to avoid doig twice the same computations
#dt2= gpd.read_file("glue2.shp")
#print("importing done")


## Read data

centers= gpd.read_file("neighbours.shp")

#print("importing done")



dt2=dt2[dt2['BU_NAAM'] != "Verspreide huizen"]


neigh= dt2[["BU_NAAM",'GM_NAAM']]
neigh=neigh.drop_duplicates()


#select the neighbourhoods present 
bu=buurt.loc[(buurt["BU_NAAM"].isin(neigh["BU_NAAM"])) & (buurt["GM_NAAM"].isin(neigh["GM_NAAM"]))]
bu = bu.reset_index()

print("lit of neigh after filter  ", len(bu))

bu=gpd.GeoDataFrame(bu)


#compute neighbourhoods within 5000 m

ind=selectNeighbours(bu,5000)

#print("ind length ", len(ind))


#add centroid column
#bu['centroid']= None

#filter all data dtfilt= filterDown(bu,ind,dt,idx[0])

#houses
dtfo=dt2[dt2["gebruiksdo"] == "woonfunctie"]   
dup= dtfo[["gid"]].drop_duplicates()
dtfo=dtfo.loc[dtfo["gid"].isin(dup["gid"])]

dtio=dt2[dt2["gebruiksdo"] == "industriefunctie"]
dup= dtio[["gid"]].drop_duplicates()
dtio=dtio.loc[dtio["gid"].isin(dup["gid"])]
    
    
#get bijeen
dtbo=dt2[dt2["gebruiksdo"] == "bijeenkomstfunctie"]
dup= dtbo[["gid"]].drop_duplicates()
    
dtbo=dtbo.loc[dtbo["gid"].isin(dup["gid"])]

#get buildings
dup= dt2[["gid"]].drop_duplicates()
dt3=dt2.loc[dt2["gid"].isin(dup["gid"])]

data = dt2.iloc[0:0]
indust=dt2.iloc[0:0]
bij= dt2.iloc[0:0]


##--------------------------getting denisty centers---------------------------------#

center1= []
center2=[]

wrongx=[]
wrongy=[]
wrnames=[] 


for x in range(len(bu)):
    #print(len(bu))
    
    #print("---------------------------------------")
    #print(bu.iloc[x,:]['BU_NAAM']," ",bu.iloc[x,:]['GM_NAAM'])
    #print(x,"out of ",len(neigh))
    #print("--------------------------------------- ")
        
    ##get index
   # idx = bu.index[(bu['BU_NAAM'] == neigh.iloc[x,:]['BU_NAAM']) & (bu['GM_NAAM'] == neigh.iloc[x,:]['GM_NAAM'])].tolist()

   # print("index ",idx)
    
    if("" != bu.iloc[x,:]['GM_NAAM']): 
        print("---------------------------------------")
        print(bu.iloc[x,:]['BU_NAAM']," ",bu.iloc[x,:]['GM_NAAM'])
        print(x,"out of ",len(neigh))
        print("--------------------------------------- ")
        #select houses in the neigh
        burgHouses=dt3[(dt3['BU_NAAM'] == bu.iloc[x,:]['BU_NAAM']) & (dt3['GM_NAAM'] == bu.iloc[x,:]['GM_NAAM']) ] 
        print("houses ", len(burgHouses))
    
    
        #get centroid an adds it to the buurt file
        centerx,centery= getDensityCenter(burgHouses,bu)
        #print("centers ", centerx," ",centery)
        
        if(bu.iloc[x].geometry.contains(Point(centerx,centery))):
            center1.append(centerx)
            center2.append(centery)
        else:
            center1.append(centerx)
            center2.append(centery)
            print("Wrong centroid")
            print("id", x )
            wrongx.append(centerx)
            wrongy.append(centery)
            
            names=[dt2.iloc[x]['BU_NAAM'],dt2.iloc[x]['GM_NAAM']]
            
            wrnames.append(", ".join(names))
    
       
bu["centroid"]= list(zip(center1, center2))
bu["centroid"]= bu["centroid"].apply(Point)
crs = {'init': 'epsg:28992'} 
bu=bu[["BU_NAAM","GM_NAAM","centroid"]]
bu = gpd.GeoDataFrame(bu,crs=crs, geometry='centroid')

print(bu.head())

bu.to_file(driver = 'ESRI Shapefile', filename= "neigh.shp")

for i in range(len(neigh)): 
    print("---------------------------------------")
    print(bu.iloc[i,:]['BU_NAAM']," ",bu.iloc[i,:]['GM_NAAM'])
    print(i,"out of ",len(neigh))
    print("--------------------------------------- ")

    dtf=filterDown(bu,ind,dtfo,i)
    print("number of houses before ", len(dtfo))
    print("number of houses after ", len(dtf))

    #filter industry data
    dti=filterDown(bu,ind,dtio,i)
    print("number of industries before ", len(dtio))
    print("number of industries ", len(dti))
    
    #filter bij data
    dtb=filterDown(bu,ind,dtbo,i)
    print("number of bij before ", len(dtbo))
    print("number of bij ", len(dtb))


    if(len(dtf)>0):
        # dtd = getWithinDist(dti,centers,300)
        dtf= countNeighbours(dtf)
        data=gpd.GeoDataFrame(pd.concat([data,dtf]))
        
        
        
    if(len(dti)>0):
       # dtd = getWithinDist(dti,centers,300)
        indust=gpd.GeoDataFrame(pd.concat([indust,dti]))
        
        #get neighbours for houses around 300m
        neighbours= countNeighbours(dtd) 
    
    if(len(dtb)>0):
        #dtdb = getWithinDist(dtb,centers,300)
        bij=gpd.GeoDataFrame(pd.concat([bij,dtb]))



#file,neigh = main(ggpol,ggp,buurt)

data.to_file(driver = 'ESRI Shapefile', filename= "houses.shp")
indust.to_file(driver = 'ESRI Shapefile', filename= "indust.shp")
bij.to_file(driver = 'ESRI Shapefile', filename= "bij.shp")

print("files saved")

