# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 09:49:21 2017

@author: gracejenkins

The purpose of this file is to run different scenarios of the simulations
"""

from Scheduling_Simulation import *

def compare_holding(static_parameters, dynamic_parameters):
    # inputs
    inputs = {}
    inputs['Daily Appointments Available'] = 10
    inputs['Days to run'] = [300]
    inputs['Warm up period'] = 30
    inputs['Urgent rates'] = [4]
    inputs['Non-urgent rates'] = [6]
    inputs['Non-urgent threshold method'] = 'Dynamic'
    inputs['Non-urgent threshold inputs'] = {}
    inputs['Non-urgent threshold inputs']['Dynamic'] = [14,1]
    
    total_demand = create_total_demand(inputs)
    
    inputs['Hold for urgent method'] = 'Static'
    inputs['Hold for urgent inputs'] = {}
    
    results = {}
    
    for parameter in static_parameters:
        # number of appointments to hold in the case of static holding 
        inputs['Hold for urgent inputs']['Static'] = parameter
        run_simulation("Milk Carton", inputs, total_demand)
        print("Milk Carton: Static ("+str(parameter)+")")
        results['Static ('+str(parameter)+ ')'] = summarize_results(inputs, total_demand)
    
    
    inputs['Hold for urgent method'] = 'Dynamic'
    for parameters in dynamic_parameters:
        
        inputs['Hold for urgent inputs']['Dynamic'] = parameters 
    
    
        run_simulation("Milk Carton", inputs, total_demand)
        print("Milk Carton: Dynamic ("+str(parameters)+")")
        results['Dynamic ('+str(parameters)+ ')'] = summarize_results(inputs, total_demand)
        
    
    ymax = get_max_y(results.values())
    for title in sorted(results.keys()):
        plot_results(title, results[title],ymax)
        

def compare_simulations(arrival_rates):
    
    inputs = {}
    inputs['Daily Appointments Available'] = 10
    inputs['Days to run'] = [300]
    inputs['Warm up period'] = 30
    inputs['Non-urgent threshold method'] = 'Dynamic'
    inputs['Non-urgent threshold inputs'] = {}
    inputs['Non-urgent threshold inputs']['Dynamic'] = [10,3]
    inputs['Hold for urgent method'] = 'Dynamic'
    inputs['Hold for urgent inputs'] = {}
    inputs['Hold for urgent inputs']['Static'] = 4
    inputs['Hold for urgent inputs']['Dynamic'] = [.05,.4,.8] 
    
    results = {}
    for arrival_rate in arrival_rates:
        
        inputs['Urgent rates'] = arrival_rate[0]
        inputs['Non-urgent rates'] = arrival_rate[1]
        
            
        total_demand = create_total_demand(inputs)
        
        # Run classic, first come first serve simulation
        run_simulation("Classic", inputs, total_demand)
        print("Classic (" + str(arrival_rate) + ")")
        results["Classic (" + str(arrival_rate) + ")"] = summarize_results(inputs, total_demand)
    
        # Run rolling horizon threshold simulation 
        run_simulation("Rolling Horizon", inputs, total_demand)
        print("Rolling Horizon (" + str(arrival_rate) + ")")
        results["Rolling Horizon (" + str(arrival_rate) + ")"] = summarize_results(inputs, total_demand)
    
        # Run milk carton threshold simulation
        run_simulation("Milk Carton", inputs, total_demand)
        print("Milk Carton (" + str(arrival_rate) + ")")
        results["Milk Carton (" + str(arrival_rate) + ")"] = summarize_results(inputs, total_demand)
        
    ymax = get_max_y(results.values())
    for title in sorted(results.keys()):
        if "Classic" in title:
            plot_results(title, results[title],ymax=None)
        else:
            plot_results(title, results[title],ymax)
            

def compare_thresholding(thresholds):
    
    inputs = {}
    inputs['Daily Appointments Available'] = 10
    inputs['Days to run'] = [300]
    inputs['Warm up period'] = 30
    inputs['Urgent rates'] = [7]
    inputs['Non-urgent rates'] = [3]
    inputs['Hold for urgent method'] = 'Dynamic'
    inputs['Hold for urgent inputs'] = {}
    inputs['Hold for urgent inputs']['Dynamic'] = [.1,.1,.7] 
    
    total_demand = create_total_demand(inputs)
    results = {}  
    inputs['Non-urgent threshold inputs'] = {}

    for threshold in thresholds: 
        
        inputs['Non-urgent threshold inputs']['Static'] = threshold
        inputs['Non-urgent threshold inputs']['Dynamic'] = [threshold,5]
        
        inputs['Non-urgent threshold method'] = 'Static'
        run_simulation("Milk Carton",inputs, total_demand)
        print("Milk Carton (Static " + str(threshold) + ")")
        results["Milk Carton (Static " + str(threshold) + ")"] = summarize_results(inputs, total_demand)
        
        inputs['Non-urgent threshold method'] = 'Dynamic'
        run_simulation("Milk Carton",inputs, total_demand)
        print("Milk Carton (Dynamic " + str(threshold) + ")")
        results["Milk Carton (Dynamic " + str(threshold) + ")"] = summarize_results(inputs, total_demand)
        
    
    ymax = get_max_y(results.values())
    for title in sorted(results.keys()):
        plot_results(title, results[title],ymax)    


### COMPARE SIMULATIONS ###
arrival_rates = [[[5],[5]],[[3],[7]],[[7],[3]],[[5],[6]],[[3],[8]],[[8],[3]],[[4],[5]],[[3],[6]],[[6],[3]]]
compare_simulations(arrival_rates)


### COMPARE HOLDING METHODS ###
#tatic_parameters = [0,1,2,3,4,5]
#dynamic_parameters = [[.05,.1,.7],[.05,.15,.7],[.05,.2,.7],[.01,.1,.7],[.05,.05,.7],[.1,.1,.7]]
#compare_holding(static_parameters, dynamic_parameters)

### COMPARE THRESHOLDING METHODS ###
#thresholds = [7,10,14,20,30]
#compare_thresholding(thresholds)

    