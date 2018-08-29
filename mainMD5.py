# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 11:09:45 2018

@author: YX
"""

import os
import MD5
import pandas as pd
path="C:\\Users\\YX\\Desktop\\train\\Images"
files=os.listdir(path)
s={}
for leifile in files:
    filepath=os.path.join(path,leifile)
    filename=os.listdir(filepath)
    for file in filename:
        p=os.path.join(filepath,file)
        a=MD5.MD5(p)
        name='Images/'+leifile+'/'+file
        if a not in s:
            s[a]=name

                

        
        
path1="C:\\Users\\YX\\Desktop\\test\\Images" 
testfile=os.listdir(path1)
m={}
for leif in testfile:
    fpath=os.path.join(path1,leif)
    fname=os.listdir(fpath)
    for f in fname:
        testp=os.path.join(fpath,f) 
        b=MD5.MD5(testp)
        name1='Images/'+leif+'/'+f
        if b in s:
            m[s[b]]=name1
        
        
            

     
w1=pd.read_csv('C:\\Users\\YX\\Desktop\\train\\Annotations\\train.csv') #读取标签路劲
w2=pd.read_csv('C:\\Users\\YX\\Desktop\\20180328-6608.csv')
for key, value in m.items():
    w2.iloc[(w2[w2.image_id==value].index.tolist())[0],:]=w1.iloc[(w1[w1.image_id==key].index.tolist())[0],:]
w2.to_csv('C:\\Users\\YX\\Desktop\\train.csv',index=False, header=True)
        
        
        
        
        

        