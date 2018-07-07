# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 12:59:35 2018

@author: jones
"""

import main
import pandas as pd



#Open list of possible detachments and generate object for each one
main.init("Necron")


faction = "Necron"

army = main.detachment("Patrol")
army.add_unit()