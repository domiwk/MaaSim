"""
Created on Fri Jun  8 17:45:28 2018

@author: Dominika Woszczyk 
This file contains the GA eps-MOEA and the description of the optimisation problem 
for the simulation
 
"""



from platypus import *
import random
from random import randint,randrange
import numpy as np
from multiprocessing import Pool, freeze_support
from sklearn.externals import joblib



    

#--------------------------------------------------------------------------------#  
#each action has a list of indicators
#and for each indicator there is a corresponding weight
class action:
    def __init__(self,indic,w):
        self.indic = indic
        self.w = w 
 
#function to create random weights
#used for testing
def getFunction():
    weights=[0]*numOfIndic
    for i in range(numOfIndic):
        w= randrange(-1, 1)
        weights[i]=w
    return weights


#create actions with their indicatos and weights  
def getActions():
    
    actions = [None]*numOfActions
    
    #print("creating actions")
    #hardcoded actions resulting from the model
    actions[0]= action([3],[-10])
    actions[1]= action([4],[-10])
    actions[2]= action([6],[10])
    
    actions[3]= action([7],[10])
    actions[4]= action([8],[-10])
    actions[5]= action([9],[-10])
    
    actions[6]= action([10],[10])
    actions[7]= action([11],[10])
    actions[8]= action([12],[10])
    actions[9]= action([26],[-10])
    
    actions[10]= action([44],[10])
    
    actions[11]= action([0,5,14,15,16,21,22,23,24,25,39,41],
    [0.458,0.668,0.603,-0.589,-0.396,0.403,0.561,0.488
    ,0.4,0.345,-0.492,-0.674])
        
    return actions

#predict the score for each neighbourhood using the Random forest model
#compute the mean to get the score of the municipality 
def blackMagic(indics):        
        return np.mean(forest.predict(indics))
        
#compute the score of the municipality 
#udpate the neighbourhood values by their 
#weights and actions
def getScore(ind):
    #copy the list value istead of reference
    newindic=neigh.copy()
    
    #for each neighbourhood
    for n in range(numOfNeigh):
        #for each action
        for i in range(len(actions)):   
        #computing the new indicator    
            for j in range(len(actions[i].indic)):
                #get the id of the indicator changed by the action
                indic= actions[i].indic[j]
                #update the indicator by the weight associate with the indicator and action
                newindic[n,indic]=neigh[n,indic] + (actions[i].w[j]*ind[n,i]*(neigh[n,indic]/100))
     
    #compute the new score 
    score = blackMagic(newindic)
    return score

class liveability(Problem):
 
    
    def __init__(self):
       super(liveability, self).__init__(1,2, 1)
       
       self.types[:] = Binary(numOfActions*numOfNeigh)
       #self.types[1] = Real(0,100)
       self.constraints[:] = ">0"
       self.directions[0] = Problem.MAXIMIZE
       self.directions[1] = Problem.MINIMIZE
       
    #the evaluate function count the number of turns
    #the feeds it to the random forest model 
    def evaluate(self, solution):
       ind = solution.variables[0]
       #print("ind", ind)
       turns=0
       for i in range(len(ind)):
            if(ind[i]==1):
                turns+=1

       ind = np.asarray(ind).reshape(numOfNeigh,numOfActions)
       #print    ind = np.asarray(ind).reshape(numOfNeigh,numOfActions)
       #print("ind ", ind)
        
       score = getScore(ind)
       #print("score ", score)
       
       #fitness functions
       solution.objectives[:] = [score,turns]
       solution.constraints[:] = [turns]
        
#--------------------MAIN----------------------------------------------------#

#constants
numOfActions=12 
numOfIndic = 45
numOfNeigh=36

#set seed for reproductability           
random.seed(a=2)

 ##import municipality indicators
##no header file
muni = np.genfromtxt('data/massrawclean2.csv',delimiter=',')

#copy the value instead of reference
municontrol=muni.copy()

# load the  RAndom Forest model from disk
filename = 'forestmodel.sav'
forest = joblib.load(filename)

##select one neighbourhood
neigh = muni[:,0:45].copy()

#create actions
actions = getActions()

print("initial score ", blackMagic(neigh))







def main():
    
    freeze_support() # required on Windows

    
    print("EpsMOEA")
    algorithm = EpsMOEA(liveability(),0.01)
    
    algorithm.run(20000)
    
    for solution in nondominated(algorithm.result):
        print(solution.objectives)        