"""
Created on Fri Jun  8 17:45:28 2018

@author: Dominika Woszczyk 

This file contains The random Forest model, as well as other 
commented regression models
-KNN
-SVC
-Perceptron
-Decision Tree


"""

from sklearn import tree
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score
import sklearn.metrics as metrics
from imblearn.over_sampling import SMOTE
from collections import Counter
from sklearn.tree import export_graphviz
from treeinterpreter import treeinterpreter as ti
from sklearn.externals import joblib

# Algorithms
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score
#----------------------------------------------------------------------------#


#normalise columns
def normalise(X):
    l= np.zeros_like(X)
    for index,i in enumerate(X.T):
        for idx,j in enumerate(i):
            if j ==max(i):
                l[idx,index]=1
            elif j == min(i):
                    l[idx,index]=0
            else:
                l[idx,index]= (j-min(i))/(max(i)-min(i))
    return l

#compute means per column
def getMean(contrib):
    newc=[]
    for i in range(len(contrib[0])):
        #print("i ",i)
        mean = np.mean(contrib[:,i])
        #print("mean ",mean)
        newc.append(mean)
    return newc 
    

#compute proportions of importance for indicators within groups
def getProportion(meanConti):
    
    #get the positive values
    meanCont=np.abs(meanConti)
    
    sumx = np.sum(np.abs(meanCont))
    print("sumx ",sumx)
    
    
    #Basic services
    ##indexes 1,2,8,11,12 
    serv= meanCont[1]+meanCont[2]+meanCont[8]+meanCont[11]+meanCont[12]
    #compute proportion of services indicator
    servprop = serv/sumx
    
    #proportion of variable 1 within services indicator
    meanCont[1]=meanCont[1]/serv
    meanCont[2]=meanCont[2]/serv
    meanCont[8]=meanCont[8]/serv
    meanCont[11]=meanCont[11]/serv
    meanCont[21]=meanCont[12]/serv
    print("service ", servprop)
    
    #Healthcare
    ##indexes 6,9,27,28
    health= meanCont[6]+meanCont[9]+meanCont[27]+meanCont[28]
    healthprop = health/sumx
    
    
    meanCont[6]=meanCont[6]/health
    meanCont[9]=meanCont[9]/health
    meanCont[27]=meanCont[27]/health
    meanCont[28]=meanCont[28]/health
    print("health ", healthprop)

    
    #Environment
    ##indexes 23,24,26,29,30,31,42,43
    env= meanCont[23]+meanCont[24]+meanCont[26]+meanCont[29]+meanCont[30]+meanCont[31]+ meanCont[42]+meanCont[43]
        
    envprop = env/sumx
    
    meanCont[23]=meanCont[23]/env
    meanCont[24]=meanCont[24]/env
    meanCont[26]=meanCont[26]/env
    meanCont[29]=meanCont[29]/env
    
    meanCont[30]=meanCont[30]/env
    meanCont[31]=meanCont[31]/env
    meanCont[42]=meanCont[42]/env
    meanCont[43]=meanCont[43]/env
 
    print("envir ", envprop)
    
    #leisure
    # 44,3,4,25
    leisure= meanCont[44]+meanCont[3]+meanCont[4]+meanCont[25]
    leisureprop = leisure/sumx
    print("leisure ", leisureprop)
    
    meanCont[44]=meanCont[44]/leisure
    meanCont[3]=meanCont[3]/leisure
    meanCont[4]=meanCont[4]/leisure
    meanCont[25]=meanCont[25]/leisure
    
    
    #Housing
    ##indexes 0,5,13->22,32->41
    housing = meanCont[0]+meanCont[5]
    for i in range(22-13+1):
        housing = housing+meanCont[i+13]
    
    for i in range(41-32+1):
        housing = housing+ meanCont[i+32]
        
    for i in range(22-13+1): 
        meanCont[i]=meanCont[i]/housing 
       
    for i in range(41-32+1):
        meanCont[i]=meanCont[i]/housing 
    
    housingprop = housing/sumx
    print("housing ", housingprop)


    res= meanCont*meanConti

    print("sum ", (np.abs(housingprop)+np.abs(leisureprop)+np.abs(healthprop)+np.abs(servprop)+np.abs(envprop)))
    
    #return indicator weights within a group
    return res



#load neighbourhoods indicators
data = pd.read_csv('data/SMOTE3NONORM.csv')

#remove neighbourhood without score
dat = data[~data.score.isnull()]

#remove neighbourhoods with a class "3"
dat = dat[~(dat.score ==3)]

dat = dat.iloc[:,0:len(dat)]

#dat = dat.drop(['water'],axis=1)
dat = dat.drop(['P_SURINAM'],axis=1)
dat = dat.drop(['residentials'],axis=1)
dat = dat.drop(['OPP_WATER'],axis=1)



#split in train and test


X_train, X_test, Y_train, Y_test = train_test_split(dat.drop(['score'],axis=1), dat['score'],
                                                  test_size = .2,
                                                  random_state=56)

names = X_train.columns

print('Original train dataset shape {}'.format(Counter(Y_train)))


#aplly SMOTE algorithm to resample minority class
sm =SMOTE(k_neighbors = 2,random_state=56)
X_res, Y_res = sm.fit_sample(dat.drop(['score'],axis=1), dat['score'])

#X_res= dat.drop(['score'],axis=1)
#Y_res=dat['score']

print('Resampled dataset shape {}'.format(Counter(Y_res)))


clf_rf = RandomForestRegressor(n_estimators=500,random_state=12)
forest =clf_rf.fit(X_res, Y_res)


#10 foldscross validation
scores = cross_val_score(forest, X_res, Y_res, cv=10)

pred = clf_rf.predict(X_res)

print('pred ', pred)

#pred = int(round(pred))

print("CROSS")
print("Mean:", scores.mean())
print("Standard Deviation:", scores.std())


prediction, bias, contributions = ti.predict(forest, X_test)


#compute indicator weights based on their contribution in the model
weights=getMean(contributions)
indicW= getProportion(weights)


# save the model to disk
filename = 'forestmodel.sav'
joblib.dump(forest, filename)


print("_--------------------------------")

'''

# Other regression algorithms

  
    # KNN
knn = KNeighborsClassifier(n_neighbors = 3)
knn =knn.fit(X_train, Y_train)

Y_pred = knn.predict(X_test)

acc_knn = round(knn.score(X_train, Y_train) * 100, 2)
print("KNN ",round(acc_knn,2,), "%")

scores = cross_val_score(knn, X_res, Y_res, cv=10, scoring = "recall_micro")

print("Scores:", scores)
print("Mean:", scores.mean())
print("Standard Deviation:", scores.std())

print("----------------------------------")

# Perceptron
perceptron = Perceptron(max_iter=5)
perc =perceptron.fit(X_train, Y_train)

Y_pred = perceptron.predict(X_test)

acc_perceptron = round(perceptron.score(X_train, Y_train) * 100, 2)
print("Perceptron ",round(acc_perceptron,2,), "%")

scores = cross_val_score(perc, X_res, Y_res, cv=10, scoring = "recall_micro")

print("Scores:", scores)
print("Mean:", scores.mean())
print("Standard Deviation:", scores.std())

print("----------------------------------")

# Linear SVC
linear_svc = LinearSVC()
lin = linear_svc.fit(X_train, Y_train)

Y_pred = linear_svc.predict(X_test)

acc_linear_svc = round(linear_svc.score(X_train, Y_train) * 100, 2)
print("Linear SVC ", round(acc_linear_svc,2,), "%")

scores = cross_val_score(lin, X_res, Y_res, cv=10, scoring = "recall_micro")

print("Scores:", scores)
print("Mean:", scores.mean())
print("Standard Deviation:", scores.std())

print("----------------------------------")

# Decision Tree
decision_tree = DecisionTreeClassifier()
dec= decision_tree.fit(X_train, Y_train)

Y_pred = decision_tree.predict(X_test)

acc_decision_tree = round(decision_tree.score(X_train, Y_train) * 100, 2)
print("Decision Tree ", round(acc_decision_tree,2,), "%")

scores = cross_val_score(dec, X_res, Y_res, cv=10, scoring = "recall_micro")

print("Scores:", scores)
print("Mean:", scores.mean())
print("Standard Deviation:", scores.std())
print ("recall ",recall_score(Y_test, Y_pred,average=None))

#print("oob score:", round(forest.oob_score_, 4)*100, "%")

print("----------------------------------")

'''

