import random
import math

# We will create all the parameters we need.

seed = 1232 # It will be use to generate the same pseudo number over and over again.
random.seed(seed)
arrival_amount = 100 # The number of clients that arrive to the hospital.
                      # This is used as our simulation is a discrete event simulation.
S = 3 # Number of nurses.
mu_a = 1.0 # Average patient arrival rate.
mu_t = 0.416666667 # Average service rate of each nurse.
mu_s = 0.16 # Average healing rate at home for stable patients.
mu_ch = 2.0 # Average healing rate at home for critical patients.
alpha = 1.0 # Alpha belong to an uniform distribution
mu_cb = 0.15625 # Average healing rate at hospital.
p1 = 0.25 # The chance of patient going home instead of hospital.
hospital_capaticy = 6 # Number of beds in hospital

# Now we will define variables that will be used to run the simulation.

number_of_patients_in_nurse_queue = 0
number_of_patients_to_be_evaluated = 0
number_of_patients_at_home = 0
number_of_patients_at_hospital = 0
number_of_patients_to_arrive = arrival_amount


# Now we will define variables that will be given as the output.
# We assume the starting time is 0.0
triage_or_hospital_empty_ratio = 0.0
triage_and_hospital_empty_ratio = 0.0
critical_going_home_ratio = 0.0
average_nurse_utilization = 0.0
average_occupied_bed = 0.0
patient_going_home_ratio = 0.0
average_healing_time = 0.0

# Now we will define variables that will be used to calculate outputs.
current_time = 0.0
amount_of_time_triage_or_hospital_is_empty = 0.0
amount_of_time_triage_and_hospital_is_empty = 0.0
total_occupied_bed_times_time = 0.0
total_number_of_patinets_treated = 0
total_number_of_patinets_treated_at_home = 0
total_number_of_critical_patinets = 0
total_number_of_critical_patinets_going_home = 0



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
    global alpha
    global mu_ch
    global number_of_patients_in_nurse_queue
    global number_of_patients_to_arrive
    global number_of_patients_to_be_evaluated
    global average_nurse_utilization
    number_of_patients_to_arrive -= 1
    number_of_patients_to_be_evaluated += 1
    if number_of_patients_to_arrive > 0:
        Add_Event(event_time+Generate_Interarrival(),1) # The arrival of next patient
    if(number_of_patients_to_be_evaluated <= S): # If there is enough nurses.
        nurse_service_time = Generate_Nurse_Service_Time()
        Add_Event(event_time+nurse_service_time,2) # The departure of patient
        average_nurse_utilization = (average_nurse_utilization*S*event_time + nurse_service_time)/(S*(event_time + nurse_service_time)) # Calculating average nurse utilization.
         
    else:
        number_of_patients_in_nurse_queue += 1 # If all nurses are busy, we put the patient ina waiting queue.It's first in first out.
    
def Departure_Triage(event_time): # To execute the departure process of a customer from a triage nurse. Event code is 2
    global number_of_patients_in_nurse_queue
    global number_of_patients_to_be_evaluated
    global number_of_patients_at_hospital
    global number_of_patients_at_home
    global total_number_of_critical_patinets
    global total_number_of_critical_patinets_going_home
    global total_occupied_bed_times_time
    global average_healing_time
    global average_nurse_utilization
    number_of_patients_to_be_evaluated -= 1

    if(random.random() > p1): # To determine whether a patient is n critical condition.
        total_number_of_critical_patinets += 1
        if(hospital_capaticy >= number_of_patients_at_hospital):
            number_of_patients_at_hospital += 1
            healing_time = Generate_Hospital_Healing_Time()
            Add_Event(event_time+healing_time,3) # The treatment in hospital.
            average_healing_time = (average_healing_time*total_number_of_patinets_treated+healing_time)/(total_number_of_patinets_treated+1) # Calculating average healing time.
            total_occupied_bed_times_time += healing_time # Calculating  total_occupied_bed_times_time. This type of calculation shouldn't lead to an error as we finish the sumilation after everyone has left the hospital.
        else:
            number_of_patients_at_home += 1
            total_number_of_critical_patinets_going_home += 1
            alpha = random.random()*0.5+1.25
            mu_ch = mu_cb * alpha
            healing_time = Generate_Home_Healing_Time('c')
            Add_Event(event_time+healing_time,4) # The treatment in home due to bed inavaiblitiy. Critical condition.
            average_healing_time = (average_healing_time*total_number_of_patinets_treated+healing_time)/(total_number_of_patinets_treated+1) # Calculating average healing time.
    else:
        number_of_patients_at_home += 1
        alpha = random.random()*0.5+1.25
        mu_ch = mu_cb * alpha
        healing_time = Generate_Home_Healing_Time('s')
        Add_Event(event_time+healing_time,4) # The treatment in home due to patient contidion. Stable Condition
        average_healing_time = (average_healing_time*total_number_of_patinets_treated+healing_time)/(total_number_of_patinets_treated+1)

            
    # Now we will appoint another departure even for a patient in waiting queue (If there is any).
    if number_of_patients_in_nurse_queue > 0:
        number_of_patients_in_nurse_queue -= 1 # One less patient in the queue.
        nurse_service_time = Generate_Nurse_Service_Time()
        Add_Event(event_time+nurse_service_time,2) # Then we appoint a eparture for that patient.
        average_nurse_utilization = (average_nurse_utilization*S*event_time + nurse_service_time)/(S*(event_time + nurse_service_time)) # Calculating average nurse utilization.

def Treated_at_Hospital(event_time): # To execute the discharge process of a customer from a bed. Event code is 3
    global number_of_patients_at_hospital
    global total_number_of_patinets_treated
    number_of_patients_at_hospital -= 1
    total_number_of_patinets_treated += 1
    
def Treated_at_Home(event_time): # To execute the discharge process of a customer from the house. Event code is 4
    global number_of_patients_at_home
    global total_number_of_patinets_treated
    global total_number_of_patinets_treated_at_home
    number_of_patients_at_home -= 1
    total_number_of_patinets_treated += 1
    total_number_of_patinets_treated_at_home += 1
    
def Advance_Time(): # To advance the time to the next imminent event in the future event list. Return whether it executed an event or not.
    global current_time
    global amount_of_time_triage_and_hospital_is_empty
    global amount_of_time_triage_or_hospital_is_empty
    if len(future_event_list) == 0:
        return False
    event_time,event_code = future_event_list.pop(0)
    
    # Now we will update some total time variables.
    # We do this before current time is updated.
    if(number_of_patients_to_be_evaluated == 0 and number_of_patients_at_hospital == 0):
        amount_of_time_triage_and_hospital_is_empty += event_time - current_time
    
    if(number_of_patients_to_be_evaluated == 0 or number_of_patients_at_hospital == 0):
        amount_of_time_triage_or_hospital_is_empty += event_time - current_time
    
    if(event_code == 1):
        Arrival(event_time)
    if(event_code == 2):
        Departure_Triage(event_time)
    if(event_code == 3):
        Treated_at_Hospital(event_time)
    if(event_code == 4):
        Treated_at_Home(event_time)
    current_time = event_time
    return True 
    
def Execute_Event(): # Iterates through the future event list and executes the next imminent process.
    pass



 
Add_Event(Generate_Interarrival(),1)
print("------------------")
print(future_event_list)
print(current_time)
print(number_of_patients_in_nurse_queue)
print(number_of_patients_at_home)
print(number_of_patients_at_hospital)
print("------------------")

while(Advance_Time()):  
    print("------------------")
    print(future_event_list)
    print(current_time)
    print(number_of_patients_in_nurse_queue)
    print(number_of_patients_at_home)
    print(number_of_patients_at_hospital)
    print("------------------")
    
triage_or_hospital_empty_ratio = amount_of_time_triage_or_hospital_is_empty/current_time

triage_and_hospital_empty_ratio = amount_of_time_triage_and_hospital_is_empty/current_time
    
critical_going_home_ratio = total_number_of_critical_patinets_going_home/total_number_of_critical_patinets
    
patient_going_home_ratio = total_number_of_patinets_treated_at_home/total_number_of_patinets_treated

average_occupied_bed = total_occupied_bed_times_time/current_time
    
print("Results:")
print("triage_or_hospital_empty_ratio:",triage_or_hospital_empty_ratio)
print("triage_and_hospital_empty_ratio:",triage_and_hospital_empty_ratio)
print("critical_going_home_ratio:",critical_going_home_ratio)
print("average_nurse_utilization:",average_nurse_utilization)
print("average_occupied_bed:",average_occupied_bed)
print("patient_going_home_ratio:",patient_going_home_ratio)
print("average_healing_time:",average_healing_time)
    
