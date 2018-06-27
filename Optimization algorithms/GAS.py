# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 17:45:28 2018

@author: Dominika Woszczyk 
This class contains the description of the
optimization problem and the the four algorithms : NSGAII, PAES,
SPAE2 and epsilon-MoEA
Experiments are made in this file

"""
#imports
from platypus import *
import random
from random import randint,randrange
import numpy as np
from multiprocessing import Pool, freeze_support
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.externals import joblib


#problem definition as a string array of binary for each neighbourhood
#each action is represented as a binary
#the only contraint is that there is at least one turn
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
       
#--------------------MAIN----------------------------------------------------#
    
if __name__ == '__main__':
    __spec__ = "None"
    
    freeze_support() # required on Windows
    
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
    filename = 'data/forestmodel.sav'
    forest = joblib.load(filename)
    
    ##select one neighbourhood
    neigh = muni[:,0:45].copy()
    
    #create actions
    actions = getActions()
    
    print("initial score ", blackMagic(neigh))
    
    
    #singular check of optimization algorithms
    '''  
    print("NSGAII")
    algorithm = NSGAII(liveability())
     
    #algorithm = NSGAII(liveability(),generator=MyGenerator(),variator=CompoundOperator(SBX(), HUX(), PM(), BitFlip()))
    algorithm.run(1000)
    
    for solution in unique(nondominated(algorithm.result)):
        print(solution.objectives)
    
    
    print("PAES")
    algorithm = PAES(liveability())
    
    algorithm.run(1000)
    
    for solution in nondominated(algorithm.result):
        print(solution.objectives)
        
        
    print("SPEA2")
    algorithm = SPEA2(liveability())
    
    algorithm.run(1000)
    
    for solution in nondominated(algorithm.result):
        print(solution.objectives)
        
    print("EpsMOEA")
    algorithm = EpsMOEA(liveability(),0.01)
    
    algorithm.run(1000)
    
    for solution in nondominated(algorithm.result):
        print(solution.objectives)
        
    '''   
    
    
    problem = liveability()
       
    algorithms = [NSGAII,PAES,SPEA2,(EpsMOEA, {"epsilon":[0.01]})]
    
    #run experiment method
    results = experiment(algorithms, problem, seeds=10, nfe=20000)
   
    print("Experiments done")
    
    #compute indicator values for each algorithm
    spread = Spread()
    spr_result = calculate(results, spread)
    display(spr_result, ndigits=3)
    
    sp = Spacing()
    sp_result = calculate(results, sp)
    display(sp_result, ndigits=3)
    
    sp = Cardinality()
    c_result = calculate(results, sp)
    display(c_result, ndigits=3)
    
    sp = Objectives()
    o_result = calculate(results, sp)
    display(o_result)
    
    
    #get Means and SD
    for i, algorithm in enumerate(results):
        print(algorithm)
        print("       SPREAD")
        
        #print(spr_result[algorithm]["liveability"]['Spread'])
        result = list(map(float, spr_result[algorithm]["liveability"]['Spread']))
        mean=   np.mean(result)
        SD = np.std(result)
        print("MEan ", mean)
        print("SD ",SD)
        
        print("       SPACiNG")
        #print(sp_result[algorithm]["liveability"]['Spacing'])
        result = list(map(float, sp_result[algorithm]["liveability"]['Spacing']))
        mean=   np.mean(result)
        SD = np.std(result)
        print("MEan ", mean)
        print("SD ",SD)
        
        print("       CARDINALITY")
        #print(c_result[algorithm]["liveability"]['Cardinality'])
        result = list(map(float, c_result[algorithm]["liveability"]['Cardinality']))
        mean=  np.mean(result,dtype=float)
        SD = np.std(result)
        print("MEan ", mean)
        print("SD ",SD)
        
        print("       MIn MAX")
        #print(c_result[algorithm]["liveability"]['Cardinality'])
        result = o_result[algorithm]["liveability"]['Objectives']
        
        #print("result ", result)
        
        res1 = [i[0] for i in result]
        #print("res ", res1)
        res2 = [i[1] for i in result]
        #print("res ", res2)
        
        mean1=  np.mean(res1,dtype=float)
        SD1 = np.std(res1)
        mean2=  np.mean(res2,dtype=float)
        SD2 = np.std(res2)
        print("MEan ", [mean1,mean2])
        print("SD ",[SD1,SD2])
    