# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 13:06:29 2018

@author: jones
"""

import pandas as pd

def init():
    detachments = pd.read_excel("./Detachments.xlsx", header=0, index_col=0)
    detachments_dict = {}
    for index, rows in detachments.iterrows():
        detachments_dict[index] = detachment_types(index, rows)