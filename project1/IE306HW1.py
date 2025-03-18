import random
import math

# We will create all the parameters we need.

seed = 1232 # It will be use to generate the same pseudo number over and over again.
random.seed(seed)
arrival_amount = 20 # The number of clients that arrive to the hospital.
                      # This is used as our simulation is a discrete event simulation.
S = 5 # Number of nurses.
mu_a = 1.0 # Average patient arrival rate.
mu_t = 1.0 # Average service rate of each nurse.
mu_s = 0.16 # Average healing rate at home for stable patients.
mu_ch = 2.0 # Average healing rate at home for critical patients.
alpha = (random.random())*0.5 + 1.25 # Alpha belong to an uniform distribution
mu_cb = alpha * mu_ch # Average healing rate at hospital.
p1 = 0.3 # The chance of patient going home instead of hospital.
hospital_capaticy = 5 # Number of beds in hospital

number_of_patients_in_nurse_queue = 0
number_of_patients_to_be_evaluated = 0
number_of_critical_patients_at_home = 0
number_of_critical_patients_at_hospital = 0
number_of_patients_to_arrive = arrival_amount



def Reverse_EXP_CDF( x, rate): # Make sure x is between 0 and 1.
    return -(math.log(1-x)/rate)

def Generate_Interarrival(rate = mu_a): # To return interarrival times of sick people arriving at the hospital.
                                       # Default rate is 1 patient per hour on average
    return Reverse_EXP_CDF(random.random(),rate)
    
def Generate_Nurse_Service_Time(rate = mu_t): # To return service times for people being served at one of the triage nurses.
    return Reverse_EXP_CDF(random.random(),rate) 

def Generate_Hospital_Healing_Time(rate = mu_cb): # To return healing times for people being treated in the hospital bed.
    return Reverse_EXP_CDF(random.random(),rate) 

def Generate_Home_Healing_Time(type,rate = 1.0):  # To return healing times for people that take self care at
                                    # home. The function takes the input s for people that were found to be in stable condition
                                    # and sent back home by the triage nurse and the input c for people that were found to be
                                    # in critical condition but could not nd a bed.
    if(type == 's'):
        return Reverse_EXP_CDF(random.random(),mu_s) # For patients in stable condition.
    if(type == 'c'):
        return Reverse_EXP_CDF(random.random(),mu_cb) # For patients in critical condition.

# Now we will generate the future event list.
future_event_list = [] # The list will contain tuples of times and event codes.
# Different events have different codes.
# 1: arrival
# 2: departure triage
# 3: treated at hospital
# 4: treated at home



def Add_Event(time,code): # time is the time of the event , code is the type of the event.
    future_event_list.append((time,code))
    i = len(future_event_list)-1 # This is done to sort things by date.
    while(i > 0):
        time1,code1 = future_event_list[i]
        time2,code2 = future_event_list[i-1]
        if(time1 < time2):
            future_event_list[i] = (time2,code2)
            future_event_list[i-1] = (time1,code1)
        i -= 1
    return

def Arrival(event_time): # To execute the arrival process of a patient to the hospital. Event code is 1
    global number_of_patients_in_nurse_queue
    global number_of_patients_to_arrive
    global number_of_patients_to_be_evaluated
    number_of_patients_to_arrive -= 1
    number_of_patients_to_be_evaluated += 1
    if number_of_patients_to_arrive > 0:
        Add_Event(event_time+Generate_Interarrival(),1) # The arrival of next patient
    if(number_of_patients_to_be_evaluated <= S): # If there is enough nurses.
         Add_Event(event_time+Generate_Nurse_Service_Time(),2) # The departure of patient
    else:
        number_of_patients_in_nurse_queue += 1 # If all nurses are busy, we put the patient ina waiting queue.It's first in first out.
    
def Departure_Triage(event_time): # To execute the departure process of a customer from a triage nurse. Event code is 2
    global number_of_patients_in_nurse_queue
    global number_of_patients_to_be_evaluated
    global number_of_critical_patients_at_hospital
    global number_of_critical_patients_at_home
    number_of_patients_to_be_evaluated -= 1
    # Not finished
    if(random.random() > p1):
        if(number_of_critical_patients_at_hospital >= hospital_capaticy):
            number_of_critical_patients_at_home += 1
            Add_Event(event_time+Generate_Hospital_Healing_Time(),3) # The treatment in hospital.
        else:
            number_of_critical_patients_at_hospital += 1
            Add_Event(event_time+Generate_Home_Healing_Time('c'),4) # The treatment in home due to bed inavaiblitiy. Critical condition.
    else:
            number_of_critical_patients_at_hospital += 1
            Add_Event(event_time+Generate_Home_Healing_Time('s'),4) # The treatment in home due to patient contidion. Stable Condition
            
    # Now we will appoint another departure even for a patient in waiting queue (If there is any).
    if number_of_patients_in_nurse_queue > 0:
        number_of_patients_in_nurse_queue -= 1 # One less patient in the queue.
        Add_Event(event_time+Generate_Nurse_Service_Time(),2) # Then we appoint a eparture for that patient.
        

def Treated_at_Hospital(event_time): # To execute the discharge process of a customer from a bed. Event code is 3
    global number_of_critical_patients_at_hospital
    number_of_critical_patients_at_hospital -= 1
    
def Treated_at_Home(event_time): # To execute the discharge process of a customer from the house. Event code is 4
    global number_of_critical_patients_at_home
    number_of_critical_patients_at_home -= 1
    
def Advance_Time(): # To advance the time to the next imminent event in the future event list. Return whether it executed an event or not.
    if len(future_event_list) == 0:
        return False
    event_time,event_code = future_event_list.pop(0)
    if(event_code == 1):
        Arrival(event_time)
    if(event_code == 2):
        Departure_Triage(event_time)
    if(event_code == 3):
        Treated_at_Hospital(event_time)
    if(event_code == 4):
        Treated_at_Home(event_time)
    return True 
    
def Execute_Event(): # Iterates through the future event list and executes the next imminent process.
    pass
 
Add_Event(Generate_Interarrival(),1)
print(future_event_list)
while(Advance_Time()):    
    print(future_event_list)
    
