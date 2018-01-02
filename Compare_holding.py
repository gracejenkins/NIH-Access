# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 10:00:28 2017

@author: gracejenkins
"""

import Scheduling_Simulation  

inputs = {}
inputs['Daily Appointments Available'] = 10
inputs['Days to run'] = 1000
inputs['Warm up period'] = 300
inputs['Non-urgent threshold'] = 14
inputs['Urgent rate'] = 4
inputs['Non-urgent rate'] = 6
    
inputs['Hold for ugent method'] = 'Static'
inputs['Hold for urgent inputs'] = {}
# number of appointments to hold in the case of static holding 
inputs['Hold for urgent inputs']['Static'] = 0
# p, c, m, q and d   parameters in the case of dynamic holding
inputs['Hold for urgent inputs']['Dynamic'] = [.75,1,7,2,10] # [p,c,m,q,d]
    
    
total_demand = create_total_demand()
    
run_simulation("Milk Carton")
plot_results("Milk Carton: Static")
print("Milk Carton: Static")
milk_results = summarize_results()
    
    
inputs['Hold for ugent method'] = 'Dynamic'
inputs['Hold for urgent inputs'] = {}
# number of appointments to hold in the case of static holding 
inputs['Hold for urgent inputs']['Static'] = 0
# p, c, m, q and d   parameters in the case of dynamic holding
inputs['Hold for urgent inputs']['Dynamic'] = [.75,1,7,2,10] # [p,c,m,q,d]
    
    