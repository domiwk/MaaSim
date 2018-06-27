# -*- coding: utf-8 -*- 


"""
Created on Fri Jun  8 17:45:28 2018

@author: Dominika Woszczyk 
This file is the core of the GUI

The logic is in python but the structue is in the kv file

"""

import geopandas as gpd 
from kivy.app import App 
from kivy.uix.label import Label 
from kivy.uix.button import Button 
from kivy.animation import Animation 
from kivy.base import runTouchApp 
from kivy.lang import Builder 
from kivy.properties import ListProperty,NumericProperty, StringProperty 
from kivy.uix.floatlayout import FloatLayout 
from kivy.uix.relativelayout import RelativeLayout 
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.stencilview import StencilView 
from kivy.uix.behaviors import ButtonBehavior 
from kivy.graphics import Mesh 
from kivy.uix.bubble import Bubble
from kivy.uix.image import Image 
from kivy.core.audio import SoundLoader, Sound
from kivy.uix.progressbar import ProgressBar
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
from kivy.vector import Vector
import numpy as np
import pandas as pd
from sklearn.externals import joblib
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex 
from kivy.factory import Factory 
from kivy.properties import BooleanProperty, ObjectProperty 
from kivy.garden.navigationdrawer import NavigationDrawer 
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget 
from kivy.core.window import Window 
from kivy.metrics import dp 
from kivy.config import Config 
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition  
from os import listdir,chdir  
import re 
from random import randint
import ga




colors = (
 'EEE4DA', 'EDE0C8', 'F2B179', 'F59563',
 'F67C5F', 'F65E3B', 'EDCF72', 'EDCC61',
 'EDC850', 'EDC53F', 'EDC22E')




tile_colors = {2**i: color for i, color in
 enumerate(colors, start=1)}
 
Config.set('input', 'mouse', 'mouse,disable_multitouch') 
 
root=None

from kivy.core.window import Window
Config.set('graphics', 'fullscreen', 'auto')

class MainInterface(FloatLayout):
    pass

 
class FirstScreen(Screen): 
    pass 
 
class SecondScreen(Screen): 
    pass 
class ThirdScreen(Screen): 
    pass
    
class FourthScreen(Screen): 
    pass 
 
class MyScreenManager(ScreenManager):
    pass
     


class CircularButton(ButtonBehavior, Widget):
    
    names = StringProperty('default')
    
    coffee = StringProperty("icons/coffee.png")
    doctor= StringProperty("icons/doctor3.png")
    hosp=StringProperty("icons/hospital.png")
    
    shops=StringProperty("icons/shops.png")
    swim=StringProperty("icons/swim1.png")
    kinder=StringProperty("icons/cubes.png")
    
    library=StringProperty("icons/library.png")
    pScho=StringProperty("icons/school2.png")
    theat=StringProperty("icons/theater.png")
    
    superm=StringProperty("icons/super2.png")
    build=StringProperty("icons/building2.png")
    forest=StringProperty("icons/forest.png")
    
    def collide_point(self, x, y):
          return Vector(x, y).distance(self.center) <= self.width / 2
      
    def on_press(self):
        
        global dbscores
        global dbscore
        
        municipality= App.get_running_app().root.ids['third'].ids['form'].ids['uc']
        neighbourhood = municipality.activeShape
        if(self.name=='coffee'):
            neighbourhood.updateIndic(44,10)
       
        elif(self.name =='lib'):
            neighbourhood.updateIndic(4,-10)
        
        elif(self.name =='doc'):
            neighbourhood.updateIndic(6,10)
            
        elif(self.name =='hosp'):
            neighbourhood.updateIndic(9,-10)
            
        elif(self.name =='swim'):
            neighbourhood.updateIndic(3,-10)
            
        elif(self.name =='kinder'):
            neighbourhood.updateIndic(11,10)
        
        elif(self.name =='school'):
            neighbourhood.updateIndic(12,10)
            
        elif(self.name =='theat'):
            neighbourhood.updateIndic(10,10)
            
        elif(self.name =='forest'):
            neighbourhood.updateIndic(3,-10)
            
        elif(self.name =='super'):
            neighbourhood.updateIndic(7,10)
            
        elif(self.name =='shops'):
            neighbourhood.updateIndic(8,-10)
            
        elif(self.name =='build')   :
            neighbourhood.updateIndic(0,0.458)
            neighbourhood.updateIndic(5,0.668)
            neighbourhood.updateIndic(14,0.603)
            neighbourhood.updateIndic(15,-0.589)
            neighbourhood.updateIndic(16,-0.396)
            neighbourhood.updateIndic(21,0.403)
            neighbourhood.updateIndic(22,0.561)
            neighbourhood.updateIndic(23,0.488)
            neighbourhood.updateIndic(24,0.4)
            neighbourhood.updateIndic(25,0.345)
            neighbourhood.updateIndic(39,-0.492)
            neighbourhood.updateIndic(41,-0.674)
        global initScores
        global initScore

        
        print("score at the button", dbscores[neighbourhood.idso])
        score, scores= blackMagic(dat)
        print("score at the button", scores[neighbourhood.idso])
        #print("score", score)
        #print("initScore ", initScore)
        print("Score change avg", (score-initScore)*1000 )
        print("Score change  avg", (score-dbscore)*1000 )
        print("Score change for neigh ", (scores[neighbourhood.idso]-initScores[neighbourhood.idso])*100 )
        print("Score change for neigh ", (scores[neighbourhood.idso]-dbscores[neighbourhood.idso])*100 )
        
        #dbscore=score
        #dbscores=scores
        
        neighbourhood.score = scores[neighbourhood.idso]
        
        aploc= App.get_running_app().root.ids['third'].ids['form']
        aploc.addTurns()
        aploc.addScore((score-dbscore)*10000)
        dbscores = scores
        dbscore = score
        
        neighbourhood.switchInfo()
        
            

class CircularProgressBar(ProgressBar):

    names = StringProperty('default')
    ellipse_image = ObjectProperty(Image(source='icons/parc.png',anim_delay=0.1))
    
    def __init__(self, **kwargs):
        super(CircularProgressBar, self).__init__(**kwargs)
    

        # Set constant for the bar thickness
        self.thickness = 15
        
        # Create a direct text representation
        self.label = CoreLabel(text="0", font_size=self.thickness)

        # Initialise the texture_size variable
        self.texture_size = None

        # Refresh the text
        self.refresh_text()

        # Redraw on innit
        self.draw()
    
        #Clock.schedule_once(self.set_value(50),1)
        
        

    def draw(self):

        with self.canvas:

            # Empty canvas instructions
            self.canvas.clear()

            #set size
            self.size=[55,55]
            
            # Draw no-progress circle
            Color(1, 1, 1)
            Ellipse(pos=self.pos, size=self.size)
            

            # Draw the inner circle (colour should be equal to the background)
            Color(1, 1, 1)
            Ellipse(texture=self.ellipse_image.texture,pos=(self.pos[0] + self.thickness / 2, self.pos[1] + self.thickness / 2),
                    size=(self.size[0] - self.thickness, self.size[1] - self.thickness))


            # Center and draw the progress text
            Color(0, 0, 0, 1)
            Rectangle(texture=self.label.texture, size=self.texture_size,
                      pos=(self.size[0]/2 -9, self.size[1] -40))

    def refresh_text(self):
        # Render the label
        self.label.refresh()

        # Set the texture size each refresh
        self.texture_size = list(self.label.texture.size)

    def set_value(self, values):
        # Update the progress bar value
        self.values = values

        print("str ", self.values)
        
        # Update textual value and refresh the texture
        self.label.text = str(int(self.values))
        self.refresh_text()

        # Draw all the elements
        self.draw()




class HoverBehavior(object):

    hovered = BooleanProperty(False)
    border_point= ObjectProperty(None)


    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return 
        pos = args[1]
        #Next line to_widget allow to compensate for relative layout
        

        inside =point_inside_polygon(pos[0],pos[1],self.vrt)
        if self.hovered == inside:
            #We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    def on_enter(self):
        pass

    def on_leave(self):
        pass


Factory.register('HoverBehavior', HoverBehavior) 
    
       
     
     
 
class InfoScreen(NavigationDrawer):
    
    habitation =  NumericProperty(0)
    TopMenu= ObjectProperty()
    
    drk= NumericProperty()
    opc = NumericProperty()
    
     
    def __init__(self,opc=0.5,drk=0,  **kwargs): 
        super(InfoScreen, self).__init__(**kwargs)
        
        self.anim_time = 0.4
        self.min_dist_to_open = 0
        self.separator_image_width = dp(drk)
     
 
    def set_anim_type(self,name): 
        self.anim_type = name 
        
    def update(self): 
        self.habitation = float(self.habitation)+1
         # using App.get_running_app()
        # .. change labl.text
        
        aploc= App.get_running_app().root.ids['third'].ids['form']
        
        aploc.addTurns()
        

class Cut_copy_paste(Bubble):
    pass


      
def point_inside_polygon(x, y, poly):
    '''Taken from http://www.ariel.com.au/a/python-point-int-poly.html
    '''
    
    #print("poly ", poly)
    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

 
class TopMenu(BoxLayout): 
    score =  NumericProperty(0)
    turns =  NumericProperty(0)
    isShownMenu = BooleanProperty(False)
    
    def __init__(self, **kwargs): 
        super(TopMenu, self).__init__(**kwargs) 
        self.turns=0 
        #self.getScore() 
        
        global appl
        
        appl = self
        
        print("created applic")
        
         
    def Ai(self): 
        ga.main()
        
    def addTurns(self):
        self.turns = self.turns+1
       
    def addScore(self,score):
        self.score = float(round(self.score+score,2))
        
    def reset(self):
        global dat
        global dbscore
        global dbscores
        global initScore
        global initScores
        
        dat = initdat
        dbscore = initScore
        dbscores = initScores
        self.turns =0
        self.score =0
        
        
        

class Neighbourhood(Widget,HoverBehavior):
     
    def __init__(self,shp,name,indic,ids,**kwargs):
        #self.app = App.get_running_app()
        Widget.__init__(self, **kwargs)
        #super(Neighbourhood, self).__init__(**kwargs)
        self.shape = shp
        self.getshape()
        self.indic= indic.values
        self.name =name
        self.score=0
        self.bubb = Bubble()
        self.idso= ids
        
        
        with self.canvas:

            
            random = randint(0, 10)
        
            color= colors[random]
            
            cast = '#'+color
            
            Color(*get_color_from_hex(cast))
            Mesh( fmt=self.vfmt,mode='triangle_fan', 
            indices=self.indices, vertices=self.vertices)
            
            self.vrt =[]
            j=0
            #print("vertices ", len(self.vertices))
            for i in range(int(len(self.vertices)/4)):  
                x= self.vertices[j]
                y= self.vertices[j+1]
                self.vrt.append([x,y])
                j= j+4
                
                
            Color(*get_color_from_hex("#FFFFFF"))
                                      
            Line(points=self.vrt,width =1)


    def updateIndic(self,indn,w):
        print("dat ", dat.iloc[self.idso,indn] )
        print("weight ",w*(dat.iloc[self.idso,indn]/10))
        dat.iloc[self.idso,indn] = dat.iloc[self.idso,indn] + w*(dat.iloc[self.idso,indn]/100)
        print("dat ", dat.iloc[self.idso,indn] )
    
    #update the indicator circle with the neighbourhood values            
    def switchInfo(self):
        values=[]
        
        
        #housing
        idx=[0,5,13,12,15,16,17,18,19,20,21,22,32,33,34,35,36,37,38,39,40,41]
        hous=0
    
    
        for i in range(len(idx)):
            hous = hous + dat.iloc[self.idso,idx[i]] * highWeights[idx[i]]
        values.append(hous)
        
        #leisure
        idx=[44,3,4,25]
        leis=0
        for i in range(len(idx)):
            leis = leis +dat.iloc[self.idso,idx[i]] *highWeights[idx[i]]
        values.append(leis)
        
        #health
        idx=[6,9,27,28]
        health=0
        for i in range(len(idx)):
            health = health +dat.iloc[self.idso,idx[i]] *highWeights[idx[i]]
        values.append(health)
        
        
        #environment        
        idx=[23,24,26,29,30,31,42,43]
        envi=0
        for i in range(len(idx)):
            envi = envi +dat.iloc[self.idso,idx[i]]*highWeights[idx[i]]
        values.append(envi)
        
        
        #services
        idx=[1,2,8,11,12 ]
        se=0
        for i in range(len(idx)):
            se = se +dat.iloc[self.idso,idx[i]] *highWeights[idx[i]]
        values.append(se)
        
        
        # assign values to bubbles
        pb=App.get_running_app().root.ids['third'].ids['form'].ids['c1'].ids['pb']
        pb.set_value(values[0]*100)
        print("house ", values[0])
        pb.draw()
        
        pb=App.get_running_app().root.ids['third'].ids['form'].ids['c2'].ids['pb']
        pb.set_value(values[1]*100)
        print("leis ", values[1])
        pb.draw()
        
        pb=App.get_running_app().root.ids['third'].ids['form'].ids['c3'].ids['pb']
        pb.set_value(values[2]*100)
        pb.draw()
        
        pb=App.get_running_app().root.ids['third'].ids['form'].ids['c4'].ids['pb']
        pb.set_value(values[3]*100)
        pb.draw()
        
        pb=App.get_running_app().root.ids['third'].ids['form'].ids['c5'].ids['pb']
        pb.set_value(values[4]*100)
        pb.draw()
        #side= aploc.ids['sidemenu']
        
        print("value ", values)
        
        
     
    #activate when a shape is clicked on
        
    def on_touch_down(self, touch):
        #  vrt= [[10,390],[10,280],[30,200],[39,190],[60,150],[40,201]]
        #print("touched somwhere")
        aploc= App.get_running_app().root.ids['third'].ids['form']
        informenu= aploc.ids['nd']
        uc= aploc.ids['uc']
        
        if point_inside_polygon(touch.x,touch.y,self.vrt):
            print("---------")
            print("name ", self.name)
            print("self id ", self.idso)
            print("score ", initScores[self.idso])
            
            uc.setActive(self,self.idso)

            print("state ", informenu.state)
            
            informenu.toggle_state()
            
            self.switchInfo()

                                                     
            
      

    def on_enter(self, *args):
        
            #print("args ", self.border_point)
            pos = self.border_point
            xy=self.to_widget(*pos)
            
            #if not hasattr(self, 'self.bubb'):
            
            self.bubb.background_color=[1,1,1,0.4]
            self.bubb.add_widget(Label(text=self.name))
            self.bubb.add_widget(Label(text=str(self.score)))
            self.bubb.size_hint: (0.01, 0.1)
            #self.add_widget(self.bubb)

            
            
    def on_leave(self,*args):
        #self.remove_widget(self.bubb)
        #self.clear_widgets()

        pass
            
                    
    def scale(self,px,py,polygon): 

        j=0 
         
        #print("before scale ", px[0]) 
         
        for i in range(len(px)-1): 
             
            scaledx= ((px[i]-minx)/ (maxx-minx))*450
             
            scaledy= ((py[i]-miny)/(maxy-miny)) *450 
            self.indices[i]=i 
            self.vertices[j]= scaledx + 270 
            self.vertices[j+1]= scaledy + 80 
            j= j+4 

         
    def center(self): 
        pass 
         
    def getVertices(self,px,py,polygon): 
        
        self.vertices =4*(len(px)-1)*[0] 
        self.indices=[0]*len(px) 
        j=0 
        #print("len ",len(px)) 
         
        #scale coordinate to be between 0-500 
        self.scale(px,py,polygon) 
 
   
    def getshape(self): 

        pointsx, pointsy= getpoints(self.shape) 
        
        self.vfmt = [
            (b'vPosition', 2, 'float'),
            (b'vCenter', 2, 'float')
            ]
        
        self.getVertices(pointsx,pointsy,geom) 

                    
                        
        
 
#class encapsulating the neighbourhoods
class Municipality(StencilView): 
    
    activeShape=None
    
 
    def __init__(self, **kwargs): 
        super(Municipality, self).__init__(**kwargs) 
        #self.getshape() 
        widg = Widget()
        
        #create neighburhoods feom shapefiles and indicators
        j=0
        for i in range(len(selected)):     
            neigh = selected.iloc[i]['geometry']
            name = selected.iloc[i]['BU_NAAM']
            indic = muni.loc[muni['BU_NAAM']==name]
            #print("i ",i)
            shape = Neighbourhood(shp=neigh, name = name,indic=indic,ids=j)
            
            if(len(indic)>0):
                j=j+1
        
            widg.add_widget(shape)
            
        self.add_widget(widg)

    #whenever an neighbourhood is clicked on, it becomes the active neighbourhood   
    def setActive(self,shape,idso):
        self.activeShape=shape
        self.activeId= idso
        
    
class testApp(App):
    
    #late initiliaser 
    def initiate(self,dt):
        
        #print(App.get_running_app().root.ids['third'].ids['form'].ids)
        
        pb=App.get_running_app().root.ids['third'].ids['form'].ids['c1'].ids['pb']
        pb.set_value(0)
        pb.ellipse_image = Image(source='icons\home.png',anim_delay=0.1)
        pb.draw()
        
        pb=App.get_running_app().root.ids['third'].ids['form'].ids['c2'].ids['pb']
        pb.set_value(0)
        pb.ellipse_image = Image(source='icons\leisure.png',anim_delay=0.1)
        pb.draw()
        
        pb=App.get_running_app().root.ids['third'].ids['form'].ids['c3'].ids['pb']
        pb.ellipse_image = Image(source='icons\heath.png',anim_delay=0.1)
        pb.set_value(0)
        pb.draw()
        
        pb=App.get_running_app().root.ids['third'].ids['form'].ids['c4'].ids['pb']
        pb.ellipse_image = Image(source='icons\envi2.png',anim_delay=0.1)
        pb.set_value(0)
        pb.draw()
        
        pb=App.get_running_app().root.ids['third'].ids['form'].ids['c5'].ids['pb']
        pb.ellipse_image = Image(source='icons\goods1.png',anim_delay=0.1)
        pb.set_value(0)
        pb.draw()

    #build the main application
    def build(self):
        self.M = Music()
        self.M.play()
        self.app = App.get_running_app()
        
        self.app.mc = SoundLoader.load('song/background.mp3')
        self.app.mc.loop = True
        self.app.mc.play()
        global root             
        root = MainInterface()
        Clock.schedule_once(self.initiate, 1)
       #self.animate()
        return root
        
 
             
             
             
             
#-------------- Import -----------------------------------# 
 
def getpoints(data): 
    data = str(data) 
    f = re.sub('[(POLYGON)]','', data) 
    points = f.split(",") 
    px=[0]*len(points) 
    py=[0]*len(points) 
     
    #print("len points ", len(points)) 
    for i in range(len(points)-1): 
        if(points[i][0]==" "): 
            points[i]=points[i][1:] 
          
        if(points[i][len(points[i])-1]==" "): 
            points[i]=points[i][0:len(points[i])-2] 
     
        x,y= (points[i].split(" ")) 
        px[i]=float(x) 
        py[i]=float(y) 
         
    return px,py 



def blackMagic(indics):
    return np.mean(forest.predict(indics)),forest.predict(indics)
   
 
def getActions():
     pass


class Music(Sound):
    def __init__(self):
        self.sound =  SoundLoader.load('song/background.mp3')   

#---------------------------------------------------------------------#

#import files
 
b=  "data/buurtlim.shp" 
buurt = gpd.read_file(b) 
#select Maastricht 
 
selected = buurt.loc[buurt['GM_NAAM']=="Maastricht"] 
 

#combine all geometry into one polygon 
muni=selected.dissolve(by='GM_NAAM') 
 
#take geometries 
geom = muni[["geometry"]] 
 
px= geom.centroid.x 
py= geom.centroid.y 
 
maxi = geom.bounds 
minx= maxi.iloc[0]["minx"] 
miny =  maxi.iloc[0]["miny"] 
         
maxx=  maxi.iloc[0]["maxx"] 
maxy= maxi.iloc[0]["maxy"] 
 
pointsx, pointsy= getpoints(geom.iloc[0]["geometry"]) 
 
#import indicators per neighbourhood
muni = pd.read_csv('data/MassrawcleanNAMES.csv')

dat = muni.iloc[:,1:len(muni.iloc[0])-1]


#copy to keep original
initdat = dat

values = muni.values


#load weights for in-game indicators
highWeights = np.genfromtxt('data/weights.csv')



#load Random Forest model
filename = 'forestmodel.sav'
forest = joblib.load(filename)
    
#municontrol=muni.copy()
initScore,initScores= blackMagic(dat)
print("initial score ", initScore)

#copy the score to keep original
dbscore = initScore
dbscores = initScores


 
#----------- Run App--------------# 
 
if __name__ == '__main__': 
  testApp().run()
    