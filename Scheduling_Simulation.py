# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 09:49:21 2017

@author: gracejenkins
"""


import numpy as np
import random
import matplotlib.pyplot as plt
from math import pi 
import sys

### The simulation ###

sys.setrecursionlimit(1500)


class Patient:

    def __init__(self,type_,day):

        self.type = type_
        self.arrival_day = day

    def create_appointment(self,day):
        self.appointment = day
        self.waittime = day - DAY 
        


class Day:

    def __init__(self,date_,inputs):

        
        self.date = date_
        self.available_appointments = inputs['Daily Appointments Available']
        self.appointments = [] 
        
    def create_appointment(self,patient):
        self.appointments += [patient]

def initialize_schedule(days_to_run, inputs):
    schedule = []
    for date_ in range(days_to_run):
        schedule += [Day(date_,inputs)]
    return schedule

def add_days(up_to_day,inputs):
    """ If the current schedule does not include days far enough in the future, adds days to the schedule"""
    
    global schedule 
    
    for day in range(up_to_day - len(schedule)+1):
        schedule += [Day(day+len(schedule),inputs)] 
        
def initilize_outputs():
    
    outputs = {}
    outputs['Urgent Wait Times'] = []
    outputs['Non-urgent Wait Times'] = []
    outputs['Unused Appointments']  = []
    
    return outputs
    

def create_demand(day, inputs, urgent_rate, nonurgent_rate):
    """ Given arrival rates for urgent and non urgent patients, creates demand 
    for urgent and non-urgent arrivals. Returns a list of patients to be assigned 
    appointments."""
    
    global outputs
    
    urgent_demand = np.random.poisson(urgent_rate)
    nonurgent_demand = np.random.poisson(nonurgent_rate)
    
    incoming_demand = []
    
    for urgent_patient in range(urgent_demand):
        incoming_demand += [Patient("urgent",day)]
    for nonurgent_patient in range(nonurgent_demand):
        incoming_demand += [Patient("nonurgent",day)]
    
    random.shuffle(incoming_demand)
    
    
    return incoming_demand

def create_total_demand(inputs): 
    """ Given the number of days to run the simulation and the arrival rate for
    urgent and non-urgent patients, creates the demand for the entire span of the 
    simulation. This is done so that in comparing scheduling methods the exact
    same demand can be used"""
    
    total_demand = []
    urgent_rate = inputs['Urgent rates'][0]
    nonurgent_rate = inputs['Non-urgent rates'][0]
    
    for day in range(inputs['Warm up period']):
        total_demand += [create_demand(day, inputs, urgent_rate, nonurgent_rate)]
    
    prev_days = inputs['Warm up period']
    
    for iteration in range(len(inputs['Days to run'])):
        period_len = inputs['Days to run'][iteration]
        urgent_rate = inputs['Urgent rates'][iteration]
        nonurgent_rate = inputs['Non-urgent rates'][iteration]
        
        for day in range(period_len):   
            total_demand += [create_demand(day+prev_days, inputs, urgent_rate, nonurgent_rate)]
        
        prev_days += period_len
        
    return total_demand 

def get_current_urgent_waittimes(inputs,total_demand):
    """ For dynamic adjustments the current average urgent waittimes of patients
    over the last 3 days is calculated. """
    
    global DAY
    
    if DAY < 3:
        return 0

    patients = total_demand[DAY-1] + total_demand[DAY-2] + total_demand[DAY-3]
    
    if len(patients) == 0:
        return 0
    
    waittimes = 0
    for patient in patients:
        if patient.type == "urgent":
            waittimes += patient.waittime
                
    avg_urgent_waittimes = waittimes/len(patients)
    
    return avg_urgent_waittimes
    
def hold_appointments(day, inputs,total_demand):
    """ Based on user inputs (static or dynamic system and the parameters), 
    calculates the number of appointments that should be held for urgent patients. 
    If it is a dynamic system, this is based on the number of days out and the 
    current average urgent wait times. """
    
    global DAY
    
    if inputs['Hold for urgent method'] == 'Static':
        return inputs['Hold for urgent inputs']['Static']
   

    days_out = day - DAY
    avg_urgent_waittimes = get_current_urgent_waittimes(inputs,total_demand)
    
    w_daysout = inputs['Hold for urgent inputs']['Dynamic'][0]
    w_urgwait = inputs['Hold for urgent inputs']['Dynamic'][1]
    max_prop = inputs['Hold for urgent inputs']['Dynamic'][2]
    
    proportion_to_hold = (2/pi)*(np.arctan(days_out*w_daysout) + np.arctan(avg_urgent_waittimes*w_urgwait))
    
    if proportion_to_hold > max_prop: 
        proportion_to_hold = max_prop
    
    number_to_hold = round(inputs['Daily Appointments Available']*proportion_to_hold)
    
    return number_to_hold
    
def nonurgent_threshold(inputs, total_demand):
    """ Based on user inputs (static or dynamic and parameters), calculates the
    non-urgent threshold. If the system is dynamic, it is based on an intercept 
    threshold and the current average waittimes multiplied by a slope."""
    
    global outputs
    
    if inputs['Non-urgent threshold method'] == 'Static':
        return inputs['Non-urgent threshold inputs']['Static']
    
    else:
        
        avg_urgent_waittimes = get_current_urgent_waittimes(inputs, total_demand)
        slope = inputs['Non-urgent threshold inputs']['Dynamic'][1] 
        intercept = inputs['Non-urgent threshold inputs']['Dynamic'][0]
        
        return intercept + round(avg_urgent_waittimes)*slope
    

def schedule_appointment(patient, day, inputs, total_demand, direction = 'Forward', hold_for_urgent = False):
    """ Given a patient, the day on which to begin looking for open appointments 
    and  the schedule, recursively assigns the patient an appointment """
    global schedule
    
    # add more days to the schedule if appointments must be scheduled further in advance
    if day > len(schedule)-1: 
        add_days(day,inputs)
    
    # if no available appointments have been found scheduling backward and the 
    # current day has been reached, schedule forward from the non-urgent threshold
    # (will only occur in the case of non-urgent patients and milk carton)
    if day < DAY: 
        day = DAY + nonurgent_threshold(inputs, total_demand)
        direction = 'Forward'
        
    # whether or not any appointments will be held for urgent patients 
    if hold_for_urgent == True:
        number_to_hold = hold_appointments(day, inputs, total_demand)
    else: 
        number_to_hold = 0
    
    # if there is an available schedule, book it
    if schedule[day].available_appointments > number_to_hold:
        schedule[day].available_appointments -= 1
        schedule[day].create_appointment(patient)
        patient.create_appointment(day)
        
    # if no available appointment, check the next day if scheduling forward
    elif direction == 'Forward':  
        schedule_appointment(patient,day+1, inputs, total_demand, direction, hold_for_urgent)
        
    # if no available appointment, check the previous day if scheduling backward
    else:
        schedule_appointment(patient,day-1, inputs, total_demand, direction, hold_for_urgent)
        
        
def assign_appointments_classic(incoming_demand,day,inputs, total_demand):
    
    """ Assigns appointments by first come, first serve. Does not distinguish between
    urgent and non-urgent patients. """
    
    global schedule, outputs
    
    for patient in incoming_demand:
        
        if patient.type == "urgent":
            schedule_appointment(patient,day,inputs, total_demand)
            if day > inputs['Warm up period']:
                outputs['Urgent Wait Times'] += [patient.waittime] 
                
        elif patient.type == "nonurgent":
            schedule_appointment(patient,day,inputs, total_demand)
            if day > inputs['Warm up period']:
                outputs['Non-urgent Wait Times'] += [patient.waittime]
            

def assign_appointments_rolling(incoming_demand, day, inputs, total_demand):
    
    """ Assigns urgent patients first come, first serve as soon as possible. 
    Assigns non-urgent patients forward after threshold"""
    
    global schedule, outputs
    
    for patient in incoming_demand:
        
        if patient.type == "urgent":
            schedule_appointment(patient,day, inputs, total_demand)
            if day > inputs['Warm up period']:
                outputs['Urgent Wait Times'] += [patient.waittime] 
                
        elif patient.type == "nonurgent":
            schedule_appointment(patient,day+nonurgent_threshold(inputs,total_demand),inputs, total_demand, hold_for_urgent = True)
            if day > inputs['Warm up period']:
                outputs['Non-urgent Wait Times'] += [patient.waittime]
        
def assign_appointments_milk(incoming_demand, day, inputs, total_demand):
    
    """ Assigns urgent patients first come, first serve as soon as possible. 
    Assigns non-urgent patients backward after threshold. If no appointments are
    found, goes forward form threshold."""
    
    global schedule, outputs
    
    for patient in incoming_demand:
        
        if patient.type == "urgent":
            schedule_appointment(patient,day,inputs, total_demand)
            if day > inputs['Warm up period']:
                outputs['Urgent Wait Times'] += [patient.waittime] 
                
        elif patient.type == "nonurgent":
            schedule_appointment(patient,day+nonurgent_threshold(inputs,total_demand), inputs, total_demand,direction = 'Backward', hold_for_urgent = True)
            if day > inputs['Warm up period']:
                outputs['Non-urgent Wait Times'] += [patient.waittime]
           
            
def next_day(inputs):
    global DAY, schedule, outputs
    
    if DAY > inputs['Warm up period']:
        outputs['Unused Appointments'] += [schedule[DAY].available_appointments]
    DAY += 1
    
    

def run_simulation(simulation_type, inputs, total_demand):
    global DAY, schedule, outputs
    
    DAY = 0
    schedule = initialize_schedule(sum(inputs['Days to run'])+inputs['Warm up period'],inputs)
    outputs = initilize_outputs()
    
    for iteration in range(sum(inputs['Days to run'])+inputs['Warm up period']):
        incoming_demand = total_demand[DAY]
        if simulation_type == "Classic":
            assign_appointments_classic(incoming_demand, DAY, inputs, total_demand)
        elif simulation_type == "Rolling Horizon":
            assign_appointments_rolling(incoming_demand, DAY, inputs, total_demand)
        elif simulation_type == "Milk Carton":
            assign_appointments_milk(incoming_demand, DAY, inputs, total_demand)
            
            
        next_day(inputs)
         
### Result Analysis ###

def create_plot(variable, title_, xlabel_, ylabel_):
    
    figure = plt.figure()

    plt.plot(variable)
    plt.ylabel(ylabel_)
    plt.xlabel(xlabel_)
    plt.title(title_)
    
    return figure

def waittimes_by_day(inputs, total_demand):
    """ Calculates average wait times by day of arrival"""
    
    
    urgent_avg_waittimes = []
    nonurgent_avg_waittimes = []
    
    for day in range(inputs['Warm up period'],len(total_demand)):
        urgent_waittimes = []
        nonurgent_waittimes = []
        for patient in total_demand[day]:
            if patient.type == "urgent":
                urgent_waittimes += [patient.waittime]
            elif patient.type == "nonurgent":
                nonurgent_waittimes += [patient.waittime]
        try:
            urgent_avg_waittimes += [sum(urgent_waittimes)/len(urgent_waittimes)]
        except:
            urgent_avg_waittimes += [None]
        try:
            nonurgent_avg_waittimes += [sum(nonurgent_waittimes)/len(nonurgent_waittimes)]
        except:
            nonurgent_avg_waittimes += [None]   
        
    return urgent_avg_waittimes, nonurgent_avg_waittimes

def get_max_y(results_list):
    
    nonurgent_max = 0
    for results in results_list:
        list_max = max(x for x in results['Non-urgent by day'] if x is not None)
        nonurgent_max = max(list_max,nonurgent_max)
        
    return nonurgent_max
    
def demand_by_type(inputs, total_demand):
    """ Calculates demand arrived by type, plots. """

    urgent_demand = []
    nonurgent_demand = []
    
    for day in range(inputs['Warm up period'], sum(inputs['Days to run'])+inputs['Warm up period']):
        urgents = 0; nonurgents = 0;
        for patient in total_demand[day]:
            if patient.type == "urgent":
                urgents += 1
            elif patient.type == "nonurgent":
                nonurgents += 1
        urgent_demand += [urgents]
        nonurgent_demand += [nonurgents]
        
    plt.figure()
    urgent, = plt.plot(urgent_demand, label = "Urgent")
    nonurgent, = plt.plot(nonurgent_demand, label = "Non-urgent")
    plt.legend(handles = [urgent, nonurgent])
    plt.xlabel("Days")
    plt.title("Demand by Patient Type")

    
def plot_results(title, results, ymax):
    
    #global outputs
    
    #create_plot(outputs["Urgent Wait Times"], title + " Urgent Wait Times","Patient","Days")
    #create_plot(outputs["Non-urgent Wait Times"], title + " Non-urgent Wait Times","Patient","Days")
    #create_plot(outputs["Unused Appointments"], title + " Unused Appointments","Day","Unused Appts.")
    urgent_avg_waittimes = results['Urgent by day']
    nonurgent_avg_waittimes = results['Non-urgent by day']
    plt.figure()
    urgent, = plt.plot(urgent_avg_waittimes, label = "Urgent Avg. Wait Time")
    nonurgent, = plt.plot(nonurgent_avg_waittimes, label = "Non-Urgent Avg. Wait Time")
    plt.legend(handles = [urgent, nonurgent])
    plt.xlabel("Days")
    plt.title(title + " Average Wait Time by Day")
    plt.ylim(ymax = ymax)
    
def summarize_results(inputs, total_demand):
    
    global outputs, schedule
    
    results = {}
    results['Average Urgent Wait Time'] = sum(outputs['Urgent Wait Times'])/len(outputs['Urgent Wait Times'])
    results['Average Non-urgent Wait Time'] = sum(outputs['Non-urgent Wait Times'])/len(outputs['Non-urgent Wait Times'])
    results['Total Unused Appointments'] = sum(outputs['Unused Appointments'])
    results['Total Patients Arrived'] = sum(len(day) for day in total_demand[inputs['Warm up period']:])
    print(results)
    
    urgent_avg_waittimes, nonurgent_avg_waittimes = waittimes_by_day(inputs, total_demand)
    # store other results, not to be printed 
    results['Urgent by day'] = urgent_avg_waittimes
    results['Non-urgent by day'] = nonurgent_avg_waittimes
    results['Urgent Wait Times'] = outputs['Urgent Wait Times'] 
    results['Non-urgent Wait Times'] = outputs['Non-urgent Wait Times'] 
    results['Unused Appointments'] = outputs['Unused Appointments'] 
    results['Schedule'] = schedule[inputs['Warm up period']:]
    results['Total Demand'] = total_demand[inputs['Warm up period']:]
    
    return results
    
if __name__ == "__main__":    
    # inputs
    inputs = {}
    inputs['Daily Appointments Available'] = 10
    inputs['Warm up period'] = 30
    inputs['Days to run'] = [100, 100, 100, 100] # for each arrival rate
    inputs['Urgent rates'] = [5,6,4,5]
    inputs['Non-urgent rates'] = [5,6,4,5]
    
    inputs['Hold for urgent method'] = 'Dynamic'
    inputs['Hold for urgent inputs'] = {}
    # number of appointments to hold in the case of static holding 
    inputs['Hold for urgent inputs']['Static'] = 6
    # p, c, m, q and d   parameters in the case of dynamic holding
    inputs['Hold for urgent inputs']['Dynamic'] = [.05,.4, .8] # days out parameter, urgent waittime parameter, max proportion
    
    inputs['Non-urgent threshold method'] = 'Dynamic'
    inputs['Non-urgent threshold inputs'] = {} 
    inputs['Non-urgent threshold inputs']['Static'] = 14
    inputs['Non-urgent threshold inputs']['Dynamic'] = [10,2] # intercept, slope
    
    
    total_demand = create_total_demand(inputs)
    demand_by_type(inputs, total_demand)
    
    # Run classic, first come first serve simulation
    run_simulation("Classic", inputs, total_demand)
    print("Classic")
    classic_results = summarize_results(inputs, total_demand)
    
    #Run rolling horizon threshold simulation 
    run_simulation("Rolling Horizon", inputs, total_demand)
    print("Rolling Horizon")
    rolling_results = summarize_results(inputs, total_demand)
    
    # Run milk carton threshold simulation
    run_simulation("Milk Carton", inputs, total_demand)
    print("Milk Carton")
    milk_results = summarize_results(inputs, total_demand)
    
    ymax = get_max_y([classic_results, rolling_results, milk_results])
    plot_results("Classic",classic_results,ymax=None)
    plot_results("Rolling Horizon",rolling_results,ymax)
    plot_results("Milk Carton",milk_results,ymax)
    
