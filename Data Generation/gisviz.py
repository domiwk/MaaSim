# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 17:32:47 2018

@author: D.C. Woszczyk

This file contains classes that compute the indicators from shapefiles

"""
#%% 
import geopandas as gpd
from sklearn.neighbors import KDTree
import pandas as pd
import time


##---------------------------------------------------------------------
#---------------------------------------------------------------------
#Functions
#get x and y  of the  geometrical centroid 
def getcoord(data):
    x = data.geometry.centroid.x
    y = data.geometry.centroid.y
    return x,y

#compute minimal distance from polygon to point
def min_distance(point, polygones):
    return polygones.distance(point).min()

#get points representing plygons points
def getpoints(data):
    return data.representative_point()

#function to count elements within distance
#making KDTree
def count(data,distance):
    data['x'],data['y']= getcoord(data)
    treedt= data[['x','y']]
    buildTree = KDTree(treedt)
    
    point =data[['x','y']]

    res = buildTree.query_radius(point,r=distance,count_only=True)

    #print("count results ",res )
    return res[len(res)-1]-1

#get the ids of elements that ae within distance in meters
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
    

#select neighbourhoods that are withing 300m of the selected neighbourhood
#returns filtered neighbourhoods
#reduces  later computations  
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

#measure the minimal distance from a point to an element
#used to get the distance from the center to roads, forests,etc
def countd(data,buurt):
    
    centroidx = buurt.centroid.x
    centroidy = buurt.centroid.y
            
    
    centroid = Point(centroidx, centroidy)
    
    dist =  min_distance(centroid, data)  

    return dist
  
#get the total surface of the polygons
# used for houses and buildings  
def getSurface(data):
    return data.area.sum()

#count the total number of elements within distance
def getTotalAround(dtf,buurt):
    filt = dtf[["geometry"]]
    
    #add centroid to age dataframe
    buurt = buurt[["geometry"]]
    data=filt.append(buurt)

    #total of all houses
    tot=count(data,200)
  
    print("total houses around 200 m :", tot)
    
    return tot

#count the numbers of neighbours
#used fr neighbourhoods and houses(to see if they are row houses o with four walls)
def countNeighbours(df):
    df["neighbors"] = None  # add NEIGHBORS column

    for index, country in df.iterrows():   
        # get 'not disjoint' countries
        neighbors = df[~df.geometry.disjoint(country.geometry)].gid.tolist()
        # remove own name from the list
        neighbors = [ gid for gid in neighbors if country.gid != gid ]
        # add names of neighbors as NEIGHBORS value
        df.at[index, "neighbors"] = ", ".join(neighbors)
        df.at[index, "neighbors"] = len(neighbors)

    return df

#buildings age ratios
#inputs : dataframe with houses, one point corresponding to the buurt and interval boundaries
def getAge(dtf,buurt,a,b,tot):
    
    #filter houses rows to be only that age interval
    
    filt = dtf.loc[(pd.to_numeric(dtf['bouwjaar']) >= a) & (pd.to_numeric(dtf['bouwjaar']) <= b)]

    if(len(filt)>0):
    #print("filtered data ", filt.head())
    
        filt = filt[["geometry"]]
        
        
        filt = filt.append(buurt)
          
        #count the houses over that age houses
        counts = count(filt,200)
        
        print("total houses with that age around 200 m :", counts)
    
        #print(filt.head())
    
        #ratio
        
        if tot ==0:
            res=0
        else:
            res = counts/tot 
    else:
        res=0

    return res

#get ratio of house with condition on type
#used for row and free 
def getRatio(dtf,buurt,total,condition):
    
    #total of all houses
    #print("total ", tot)
    
    filt = dtf[dtf['building'] == condition]
    filt = filt[["geometry"]]
    
    if(len(filt)>0):
    
        filt = filt.append(buurt)
        
        
        
        #count the houses over that age houses
        counts = count(filt,200)
        
        print("total ",total)
        print("houses with age ", counts,"that are ",condition)
    
        #ratio
        if(total==0):
            res=0
        else:   
            res= counts/total
    else:
        res=0

    return res

#compute the ration or industrie and meeting buildings
def getRatioOther(dtf,indic, buurt):
    filt = dtf[["geometry"]]
    ind= indic[["geometry"]]
    
    if(len(filt)>0):
        #add centroid to age dataframe
        buurt = buurt[["geometry"]]
        data=filt.append(buurt)
    
        #total of all houses
        tot=count(data,200)
        
        #print("total ", tot)
           
        #count industrie
        if(len(ind)>0):
    
            #add centroid to age dataframe
            data=ind.append(buurt)
        
            #total of all houses with function
            counts=count(data,200)
            
            if tot ==0:
                res=0
            else:
                res = counts/tot
        else:
            res=0
            
    else:
        res=0
    
    #print("indic ", tot)
    return res


#get elements around distance    
def getWithinDist(data,buurt,distance):
    buurt = buurt[["geometry"]]
    
    houses= data[["geometry"]]
    
    houses.append(buurt)
    
    #get houses id  within 200m
    filthouses = getIdAround(houses,distance)
    filthouses=  filthouses[len(filthouses)-1]
    
    cols = ['osm_id',]
    lst = []
    
    gid= pd.DataFrame(columns=['osm_id'])
    
    for i in range(len(filthouses)):
        #print("ind[x] ", ind[x])
        #print("i ",i)
        #print(dist[len(data)-1][i])
        #gid= data.iloc[i]["gid"]
        gid= data.iloc[i]["osm_id"]
        
        lst.append([gid])
        
       
    ids = pd.DataFrame(lst, columns=cols)  
    
    res= data.loc[(data["osm_id"].isin(ids["osm_id"]))]      
    print("houses collected")
    return res
    
#compute the footprint of houses
#footprint defined in Leefbaarometer 2.0 report
def footprint(housesf,buurt):
    
    res=getWithinDist(housesf,buurt,200)
      #total surface of those houses
    if len(res)!=0:
        
        s = getSurface(res)
    else:
        s=0
      
    return s
    
    
#compute the dominance of building type
#dominance defined in Leefbaarometer 2.0 report    
def dominance(data,buurt,a,b,total,totalsurf):
    
    #get share of house that have that age
    h=getAge(data,buurt,a,b,total)
    
    #get surface of house wih thaT AGE
    filt = data.loc[(pd.to_numeric(data['bouwjaar']) >= a) & (pd.to_numeric(data['bouwjaar']) <= b)]
    #print("Get surface of houses with age around")
    print("houses with that age: ",len(filt) )
    
    if(len(filt)==0):
        f=0
    else:
        f=footprint(filt,buurt)
    
    if(totalsurf!=0):
        s= f/totalsurf
    else:
        s=0

    #get average 
    res= ((h+s)/2)

    if((h+s)==0):
        res=0
    
    return res
    
#building types 
#taking as input : the buildings and the adresses
def assignType(data):   
    #assigning housing types
    #count how many neighbourhing buildings
    
    data['building']="e"
    
    #row = 2 neighbours
    #free = no neighbours
    data["building"][data['neighbors'] == "0"]="free"
    data["building"][data['neighbors'] == "2"]="row"

    return data
    

#dummies 
    
##count number of element within distance and return boolean array

def dummyCount(buurt,file,distance):
    
    
        filec=file[["geometry"]]
        #add centroid to file elements 

        bug = buurt[["geometry"]]
        
        #data = filec.append(bug)
        res=0
        
        #count how many there are within distance 
        dist = countd(filec,bug)
        
        #print("dist ",dist)
    
        if dist<=distance:
            res=1
        else:
            res=0
        
        #print("dummy : ",res)
        return res

#get the monument density within 200m around the centre
def getMonDens(monuments,buurt):

    
    bug = buurt[["geometry"]]
    
    data = monuments.append(bug)
    c= count(data,200)

    return (c/100)


##general method / wrap up
def getDummies(data,tracks,ground,roads,waters):
    #filter to only get elements for each house 
    
    print("data", data)
    
    #print("residential")
    ##residential
    res= ground.loc[ground['fclass'] == "residential"]
 
    #res = dummyCount(data,res,25)
    res = getDistanceTo(data,res)

    #print("rail")
    ##tracks
    tr= tracks.loc[tracks['fclass'] == "rail"] 
    #train = dummyCount(data,tr,25)
    train =getDistanceTo(data,tr)

    #print("parc")
    ##parc
    pa = ground.loc[(ground['fclass'] == "grass") | (ground['fclass'] == "park")] 
    #parc = dummyCount(data,pa,25)
    #parc2 =getDistanceTo(data,pa)
    parc = getWithinDist(pa,data,200)
    parc2 = getSurface(parc)
    
    
    #print("recreational")
    ##recreational
    rec= ground.loc[ground['fclass'] == "recreation_ground"] 
    #rec = dummyCount(data,rec,25)
    rec = getDistanceTo(data,rec)
    
    #print("farms")
    ##recreational
    far= ground.loc[ground['fclass'] == "farm"] 
    #farm = dummyCount(data,far,25)
    farm = getDistanceTo(data,far)
    
    #print("forest")
    ##forest
    fores= ground.loc[ground['fclass'] == "forest"] 
    fores = getDistanceTo(data,fores)
    
    
    #print("industrie")
    ##forest
    ind= ground.loc[ground['fclass'] == "industrial"] 
    #industrie = dummyCount(data,ind,25)
    industrie = getDistanceTo(data,ind)
    

    #print("roads")
    #road
    roar= roads.loc[roads['fclass'] == "primary"] 
    road = getDistanceTo(data,roar)
    
    #print("highway")
    #hghway
    roar= roads.loc[roads['fclass'] == "motorway"] 
    motor = getDistanceTo(data,roar)
    
    #print("water")
    #hghway
    #print("water type ", type(waters))
    wat= waters.loc[(waters['fclass'] == "river") & (waters['name'] == "Meuse") | (waters['name'] == "Rhein")]
    #water = dummyCount(data,wat,200)
    water = getDistanceTo(data,wat)
    
    #restrict the maximum distance to be max 5000 meters
    return train,min(res,5000),parc2,min(rec,5000),min(fores,5000),min(road,5000),min(motor,5000),min(farm,5000),min(water,5000),min(industrie,5000)
 


def getDistanceTo(buurt,element):
    
        element=element[["geometry"]]
        #add centroid to file elements 

        bug = buurt[["geometry"]]
        
        #count how many there are within distance 
        dist = countd(element,bug)
    
        return dist
    
#join two shapefiles on an common criteria
def fileglue(file1,file2):
       glued= gpd.sjoin(file1, file2,how="inner", op='intersects') 
       return glued
  
    

 #Filter down to neighbourhoods present in the input list 
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
    
    

#main method to compute the indicators for each neighbourhood
def getem(dt,indust,bij,buurts,centers,tracks,land,mon,road,waters): 
    final = []

    print("Hello")
    #print(neigh.head())

    dt=dt[dt['BU_NAAM'] != "Verspreide huizen"]
    neigh= dt[["BU_NAAM",'GM_NAAM']]
    neigh=neigh.drop_duplicates()


    print("lit of neigh before filter  ", len(buurts))

    #select the neighbourhoods present 
    bu=buurts.loc[(buurts["BU_NAAM"].isin(neigh["BU_NAAM"])) & (buurts["GM_NAAM"].isin(neigh["GM_NAAM"]))]
    bu = bu.reset_index()

    print("lit of neigh after filter  ", len(bu))

    bu= gpd.GeoDataFrame(bu)

    #select neighbourhoods within 5000 m
    ind=selectNeighbours(bu,5000)


    #select houses
    dtfo=dt[dt["gebruiksdo"] == "woonfunctie"]

    dup= dtfo[["gid"]].drop_duplicates()
    dtfo=dtfo.loc[dtfo["gid"].isin(dup["gid"])]
    

    #get industries
    dtio=dt[dt["gebruiksdo"] == "industriefunctie"]
    dup= dtio[["gid"]].drop_duplicates()
    dtio=dtio.loc[dtio["gid"].isin(dup["gid"])]


    #get meeting
    dtbo=dt[dt["gebruiksdo"] == "bijeenkomstfunctie"]
    dup= dtbo[["gid"]].drop_duplicates()

    dtbo=dtbo.loc[dtbo["gid"].isin(dup["gid"])]


    #get buildings
    dup= dt[["gid"]].drop_duplicates()
    dt=dt.loc[dt["gid"].isin(dup["gid"])]


    #print(dtf.head())



    fi = 0
     #for each buurt in the list 
    for x in range(len(neigh)):
        print("---------------------------------------")
        print(bu.iloc[x,:]['BU_NAAM']," ",bu.iloc[x,:]['GM_NAAM'])
        print(x,"out of ",len(neigh))
        print("--------------------------------------- ")

        if(x>20000):
            print("we skip this one")
        else:                
            #filter data to get centroid of the municipality
            #b= bu[(bu['BU_NAAM'] == neigh.iloc[x,:]['BU_NAAM']) & (bu['GM_NAAM'] == neigh.iloc[x,:]['GM_NAAM']) ] 
            
            b= centers[(centers['BU_NAAM'] == bu.iloc[x,:]['BU_NAAM']) & (centers['GM_NAAM'] == bu.iloc[x,:]['GM_NAAM']) ] 
            
            
            buurtInfo = bu[(bu['BU_NAAM'] == bu.iloc[x,:]['BU_NAAM']) & (bu['GM_NAAM'] == bu.iloc[x,:]['GM_NAAM']) ]
            
            #b= buurts[(buurts['BU_NAAM'] == "Cadier") & (buurts['GM_NAAM'] =="Eijsden-Margraten") ]
            
            print(b)
            
            #get index
            #idx = bu.index[(bu['BU_NAAM'] == bu.iloc[x,:]['BU_NAAM']) & (bu['GM_NAAM'] == neigh.iloc[x,:]['GM_NAAM'])].tolist()
        # print("idx ", idx[0])
            
        
        #filter all data 
            dtfilt= filterDown(bu,ind,dt,x)

            #filter house data
            dtf=filterDown(bu,ind,dtfo,x)
            print("number of houses before ", len(dtfo))
            print("number of houses after ", len(dtf))


            
            #filter industry data
            dti=filterDown(bu,ind,indust,x)
            print("number of industries before ", len(indust))
            print("number of industries ", len(dti))
            
            #filter bij data
            dtb=filterDown(bu,ind,bij,x)
            print("number of bij before ", len(bij))
            print("number of bij ", len(dtb))
            
            
            
            print("---------values filtered-----------")
            print("")
            #print(b)
        
        
            
            ##-------age buildings ratios  ----------------------------------------------
                
            #for each age interval count the ratios

            #print("total houses :")
            total =getTotalAround(dtf,b)
            
            
            #print("")
            #print("house ages before 1945")
            age00s=getAge(dtf,b,0,1945,total)     
            ratio00 = age00s
            #print("----****-----")
            
            '''
            ##1900-1920
            print("house ages 1900-1920")
            age00_20=getAge(dtf,b,1900,1920,total)  
            print("----****-----")
            
            ##1920-1945
            age00s=getAge(dtf,b,1920,1945,total)     
            ratio20_45 = age00s
            '''
            ##1945-1960
            age45_60=getAge(dtf,b,1945,1960,total)
            
            
            ##1961-1981
            age00s=getAge(dtf,b,1961,1981,total)     
            ratio60_70=age00s
            
            '''
            #1971-1981
            age71_81=getAge(dtf,b,1971,1981,total)
            
            '''
            #1991-2019
            age91_00=getAge(dtf,b,1991,2019,total)  
            
            '''
            #after 2000
            age00=getAge(dtf,b,2000,2005,total)  
            
            ##2000-2005
            age00s=getAge(dtf,b,2000,2005,total)     
            ratio2000_2005= age00s
            '''
            print("house ages done")
            print("")
            
            #get total surface 
            #total surface
            print("get total surface")
            totalsurf=footprint(dtf,b) 
        
            
            
            #before 1900
            print("------Dominance 1--------")
            dom1900=dominance(dtf,b,0,1900,total,totalsurf)
            
            #1945-1960
            print("----------Dominance 2-------")
            dom45_60 =dominance(dtf,b,1945,1960,total,totalsurf)
            
            ##1960-1970
            print("------Dominance 3--------")
            dom60_70=dominance(dtf,b,1960,1970,total,totalsurf)
            
            ##1980-1985
            print("-----Dominance 4------")
            dom80_85 = dominance(dtf,b,1980,1985,total,totalsurf)
            
            ##after 1900
            print("-----Dominance 5------")
            dom1900= dominance(dtf,b,1900,2030,total,totalsurf)
            
            print("dominances  done")
        
        #-----------Free vs row----------------------------------------------------------#
        
            
            #d = dtf[(dtf['BU_NAAM'] == neigh.iloc[x,:]['BU_NAAM']) & (dtf['GM_NAAM'] == neigh.iloc[x,:]['GM_NAAM']) ]  

        
            #neighbours= countNeighbours(d)
            d=assignType(dtf)
            
            #print(d.head())        
                        
            ratiofree=getRatio(d,b,total,"free")
            
            ratiorow=getRatio(d,b,total, "row")
        
            
        #--------- Monuments --------------------------------------------------------#    
            #monument density 
            #clean monuments
            monc = mon[["geometry"]]
            
            mon_dens= getMonDens(monc,b)

            print("monuments done")
            
            
        #---------- Industie and bij ----------------------------------------------#
            indr=getRatioOther(dtfilt,dti,b)
            bijr =getRatioOther(dtfilt,dtb,b)
            
            #print("industries and bij done")

            
        #------#for each dummy -------------------------------------------------------
            rails,resi,parcs,rec,forest,roads,motor,farm,water,industrie= getDummies(b,tracks,land,road,waters)
            
            #print("dummies done")

        
        #select indicators from buurt that are already there
        #from buurt dataset
        
        
            dat1 = buurtInfo.iloc[:,29:40]
            #print("data with demographics")
            #print(dat1.head())
            
            dat2= buurtInfo[["BU_NAAM","GM_NAAM","BEV_DICHTH","OPP_WATER","AV1_CAFE","AF_TREINST","AF_OVERST","AF_ZWEMB","AF_BIBLIO","P_SOCMINH",
                "AV3_ARTSPR","AV1_SUPERM","AF_DAGLMD","AF_ZIEK_I","AF_POP","AV1_KDV","AV1_ONDBAS","AV1_RESTAU"]]
        
            #print("data with others")
            #print(dat2.head())
            
            dat=pd.concat([dat2, dat1], axis=1)
            #print("data concatenated")
            #print(dat.head())
            
            
        #append each indicator to final dataframe    
            
            dat["rail"]=rails
        
            
            dat["residentials"]=resi
        
            dat["recreational"]=rec
            dat["forest"]=forest  
            dat["motor"]=motor
            dat["road"]=roads 
            dat["water"]=water
            dat["agric"]=farm 
            dat["industrie"]=industrie 
            
            dat["parcs"]=parcs
            dat["monu_dens"]=mon_dens
            
            
            dat["houses_before45"]=ratio00
            #dat["houses20_45"]=ratio20_45
            dat["houses60_81"]=ratio60_70
            #dat["houses2000_2005"]=ratio2000_2005
            #dat["houses1900_1920"]=age00_20
            dat["houses45_60"]=age45_60
            #dat["houses71_81"]=age71_81
            dat["houses_after91"]=age91_00
            #dat["houses2000"]=age00
        
            dat["dom45_60"] = dom45_60
            dat["dom60_70"] = dom60_70
            dat["dom80_85"] = dom80_85
            dat["dom1900"] = dom1900
            
            
            dat["ratiofree"]=ratiofree
            dat["ratiorow"]=ratiorow
            
            
            dat["ratioindustrie"] = indr
            dat["ratiomeeting"] = bijr 
            
            
            final.append(dat)
            print(" ")
        
            
    terminal= pd.concat(final)
    return terminal
  
 # %%    
 #---------------------------------------------------------------------------------------   
 #---------------------------------------------------------------------------------------
#%% 
#Main code   
 
start_time = time.time()
 

#---------Import ---------------------------------------------------------------#


##buurt shapes
b= "data/buurtlim2.shp"
 
##landuse 

land="data/landlimp.shp"

##traintracks

train ="data/raillimp.shp" 

#road
road = "data/roadlimp.shp"
  
#monuments

mon= "data/monlimp.shp"

#water
wat= "data/waterp.shp"


# Read data

buurts = gpd.read_file(b)

land= gpd.read_file(land)

tracks=gpd.read_file(train)

road =gpd.read_file(road)

mon = gpd.read_file(mon)

waters = gpd.read_file(wat)


dt= gpd.read_file("data/houses.shp")
indust= gpd.read_file("data/indust.shp")
bij= gpd.read_file("data/bij.shp")

centers= gpd.read_file("data/neighbours.shp")

print("importing done")


terminal = getem(dt,indust,bij,buurts,centers,train,land,mon,road,waters)
  
 
#save results as csv 
terminal.to_csv("indicEgTEmp.csv", sep=',')

elapsed_time = time.time()-start_time

print("elapsed time: ",elapsed_time)






