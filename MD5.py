# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 11:03:08 2018

@author: YX
"""
def MD5(file):
    import hashlib
    md5_value = hashlib.md5()
    with open(file,"rb") as file:
        while True:
            data=file.read(4096);
            if not data:
                break
            md5_value.update(data)
    return md5_value.hexdigest()
           
    
    
    