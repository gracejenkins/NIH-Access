"""
Author: Grace Jenkins

"""

import numpy as np
import random
import matplotlib.pyplot as plt

### The simulation ###

class Patient:

    def __init__(self,type_):

        self.type = type_

    def create_appointment(self,day):
        self.appointment = day
        self.waittime = day - DAY 
        


class Day:

    def __init__(self,date_):

        self.date = date_
        self.available_appointments = 5
        self.appointments = [] 
        
    def create_appointment(self,patient):
        self.appointments += [patient]

def initialize_schedule(days_to_run):
    schedule = []
    for date_ in range(days_to_run):
        schedule += [Day(date_)]
    return schedule

def add_days(up_to_day):
    
    global schedule 
    
    for day in range(up_to_day - len(schedule)+1):
        schedule += [Day(day+len(schedule))] 

def create_demand():
    """ Given arrival rates for urgent and non urgent patients, creates demand 
    for urgent and non-urgent arrivals. Returns a list of patients to be assigned 
    appointments."""
    
    global urgent_rate, nonurgent_rate, patient_list
    
    urgent_demand = np.random.poisson(urgent_rate)
    nonurgent_demand = np.random.poisson(nonurgent_rate)
    
    incoming_demand = []
    
    for urgent_patient in range(urgent_demand):
        incoming_demand += [Patient("urgent")]
    for nonurgent_patient in range(nonurgent_demand):
        incoming_demand += [Patient("nonurgent")]
    
    random.shuffle(incoming_demand)
    
    # update global variables
    patient_list.extend(incoming_demand)
    
    return incoming_demand

def schedule_appointment(patient, day, held_appointments):
    """ Given a patient, the day on which to begin looking for open appointments 
    and  the schedule, recursively assigns the patient an appointment """
    
    global schedule
    
    if day > len(schedule)-1: 
        add_days(day)
    
    if schedule[day].available_appointments > held_appointments:
        schedule[day].available_appointments -= 1
        schedule[day].create_appointment(patient)
        patient.create_appointment(day)

        
        return schedule 
    else: 
        schedule_appointment(patient,day+1,held_appointments)
        
    

def assign_appointments(incoming_demand,day):
    global urgent_waittimes, nonurgent_waittimes, schedule
    
    for patient in incoming_demand:
        if patient.type == "urgent":
            schedule_appointment(patient,day,0)
            urgent_waittimes += [patient.waittime] 
        elif patient.type == "nonurgent":
            schedule_appointment(patient,day+nonurgent_threshold,hold_for_urgent)
            nonurgent_waittimes += [patient.waittime]
            
def next_day():
    global DAY, schedule, unused_appointments
    
    unused_appointments += [schedule[DAY].available_appointments]
    DAY += 1

def run_simulation(days_to_run):
    global DAY
    for interation in range(days_to_run):
        incoming_demand = create_demand()
        assign_appointments(incoming_demand, DAY)
        next_day()
         
### Result Analysis ###

def create_plot(variable, title_, xlabel_, ylabel_):
    
    figure = plt.figure()

    plt.plot(variable)
    plt.ylabel(ylabel_)
    plt.xlabel(xlabel_)
    plt.title(title_)
    
    return figure

def waittimes_by_day(schedule):
    
    urgent_avg_waittimes = []
    nonurgent_avg_waittimes = []
    
    for day in schedule:
        urgent_waittimes = []
        nonurgent_waittimes = []
        for patient in day.appointments:
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
        
    figure = plt.figure()
    urgent, = plt.plot(urgent_avg_waittimes, label = "Urgent Avg. Wait Time")
    nonurgent, = plt.plot(nonurgent_avg_waittimes, label = "Non-Urgent Avg. Wait Time")
    plt.legend(handles = [urgent, nonurgent])
    
    return figure
    
if __name__ == "__main__":    
    # inputs
    days_to_run = 100
    urgent_threshold = 5
    nonurgent_threshold = 14
    urgent_rate = 2
    nonurgent_rate = 3
    hold_for_urgent = 2
    
        # initialize global variables
    DAY = 0
    schedule = initialize_schedule(days_to_run)
    patient_list = []
    urgent_waittimes = []
    nonurgent_waittimes = []
    unused_appointments = []
    
    
    run_simulation(days_to_run)
    create_plot(urgent_waittimes, "Urgent Wait Times","Patient","Days")
    create_plot(nonurgent_waittimes, "Non-Urgent Wait Times","Patient","Days")
    create_plot(unused_appointments, "Unused Appointments","Day","Unused Appts.")
    waittimes_by_day(schedule)