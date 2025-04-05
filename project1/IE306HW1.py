import numpy # random didn't have normal distibution in it so we had to use numpy
import random
import math

# We will create all the parameters we need.

run_multiple_times = True # To detertmine whether we run the simulation only once or not.
number_of_runs = 20 # only relevant if we are running it multiple times.
confidence_level = 0.95 # The confidence interval of our results if we run multiple times.

# the seed : 4044800276
seed = 4044800276 # It will be use to generate the same pseudo number over and over again.
random.seed(seed)
arrival_amount = 200 # The number of clients that arrive to the hospital.
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

# We also need the mean and S values of these output variables. To do that we will put them in lists.
triage_or_hospital_empty_ratio_list = []
triage_and_hospital_empty_ratio_list = []
critical_going_home_ratio_list = []
average_nurse_utilization_list = []
average_occupied_bed_list = []
patient_going_home_ratio_list = []
average_healing_time_list= []

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

event_names = ["","arrival","departure triage","treated at hospital","treated at home"] # For display

def Display_Future_Event_List(): # This function is added for the sule purpose of increasing the readibility of the output.
    print("future event list:")
    if(len(future_event_list) == 0):
        print("list is empty")
    for element in future_event_list:
        time,code = element
        print("time:",time,"\tevent:",event_names[code])
    print("---")
    
def Display_Current_State(): # This function exists to make displaying output easier
    global current_time
    global number_of_patients_to_be_evaluated
    global number_of_patients_in_nurse_queue
    global number_of_patients_at_home
    global number_of_patients_at_hospital
    print("------------------")
    Display_Future_Event_List()
    print("current time:",current_time)
    print("number of patients to be evaluated:",number_of_patients_to_be_evaluated)
    print("number of patients in nurse queue:",number_of_patients_in_nurse_queue)
    print("number of patients at home:",number_of_patients_at_home)
    print("number of patients at hospital:",number_of_patients_at_hospital)
    print("------------------")
    return

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
    global alpha
    global mu_ch
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
    # Didn't need to add anything here as advancing time also executes events.
    pass


    

# Now we will determine whether we will run the simulation once or multiple time.

if (run_multiple_times == False):
    current_time = 0.0 # To reset the simulation.
    Add_Event(Generate_Interarrival(),1)
    Display_Current_State()

    while(Advance_Time()):  
        Display_Current_State()
    
    triage_or_hospital_empty_ratio = amount_of_time_triage_or_hospital_is_empty/current_time
    triage_and_hospital_empty_ratio = amount_of_time_triage_and_hospital_is_empty/current_time
    critical_going_home_ratio = total_number_of_critical_patinets_going_home/total_number_of_critical_patinets
    patient_going_home_ratio = total_number_of_patinets_treated_at_home/total_number_of_patinets_treated
    average_occupied_bed = total_occupied_bed_times_time/current_time
    
    print("Results:")
    print("triage or hospital empty ratio:",triage_or_hospital_empty_ratio)
    print("triage and hospital empty ratio:",triage_and_hospital_empty_ratio)
    print("critical going home ratio:",critical_going_home_ratio)
    print("average nurse utilization:",average_nurse_utilization)
    print("average occupied bed:",average_occupied_bed)
    print("patient going home ratio:",patient_going_home_ratio)
    print("average healing time:",average_healing_time)
else: # If there are multiple runs, we will calculate the mean and S value of outputs to create a confidence interval
    number_of_runs_executed = 0 # it determines how many runs have been executed so far. also used for seed generation.
    while(number_of_runs_executed < number_of_runs):
        random.seed(seed+number_of_runs_executed) # To reset the seed.
        number_of_patients_to_arrive = arrival_amount # To reset the patients.
        current_time = 0.0 # To reset the simulation.
        # Now we will reset all the variables that are used to calculate the outputs and the outputs themselves
        triage_or_hospital_empty_ratio = 0.0
        triage_and_hospital_empty_ratio = 0.0
        critical_going_home_ratio = 0.0
        average_nurse_utilization = 0.0
        average_occupied_bed = 0.0
        patient_going_home_ratio = 0.0
        average_healing_time = 0.0
        
        amount_of_time_triage_or_hospital_is_empty = 0.0
        amount_of_time_triage_and_hospital_is_empty = 0.0
        total_occupied_bed_times_time = 0.0
        total_number_of_patinets_treated = 0
        total_number_of_patinets_treated_at_home = 0
        total_number_of_critical_patinets = 0
        total_number_of_critical_patinets_going_home = 0
        Add_Event(Generate_Interarrival(),1)
        while(Advance_Time()): # We are advancing through events  
            pass
        # Now we will calculate the output of each run.
        triage_or_hospital_empty_ratio = amount_of_time_triage_or_hospital_is_empty/current_time
        triage_and_hospital_empty_ratio = amount_of_time_triage_and_hospital_is_empty/current_time
        critical_going_home_ratio = total_number_of_critical_patinets_going_home/total_number_of_critical_patinets
        patient_going_home_ratio = total_number_of_patinets_treated_at_home/total_number_of_patinets_treated
        average_occupied_bed = total_occupied_bed_times_time/current_time
        
        # Then we will fill our output lists.
        triage_or_hospital_empty_ratio_list.append(triage_or_hospital_empty_ratio)
        triage_and_hospital_empty_ratio_list.append(triage_and_hospital_empty_ratio)
        critical_going_home_ratio_list.append(critical_going_home_ratio)
        average_nurse_utilization_list.append(average_nurse_utilization)
        average_occupied_bed_list.append(average_occupied_bed)
        patient_going_home_ratio_list.append(patient_going_home_ratio)
        average_healing_time_list.append(average_healing_time)
        
        number_of_runs_executed += 1
        
    # Now it's time to calculate the means , S values and confidence intervals.
    triage_or_hospital_empty_ratio_mean = 0.0
    triage_and_hospital_empty_ratio_mean = 0.0
    critical_going_home_ratio_mean = 0.0
    average_nurse_utilization_mean = 0.0
    average_occupied_bed_mean = 0.0
    patient_going_home_ratio_mean = 0.0
    average_healing_time_mean = 0.0
    
    triage_or_hospital_empty_ratio_variance = 0.0
    triage_and_hospital_empty_ratio_variance = 0.0
    critical_going_home_ratio_variance = 0.0
    average_nurse_utilization_variance = 0.0
    average_occupied_bed_variance = 0.0
    patient_going_home_ratio_variance = 0.0
    average_healing_time_variance = 0.0
    
    triage_or_hospital_empty_ratio_interval = [0.0,0.0]
    triage_and_hospital_empty_ratio_interval = [0.0,0.0]
    critical_going_home_ratio_interval = [0.0,0.0]
    average_nurse_utilization_interval = [0.0,0.0]
    average_occupied_bed_interval = [0.0,0.0]
    patient_going_home_ratio_interval = [0.0,0.0]
    average_healing_time_interval = [0.0,0.0]
    
    # Now we will calculate means.
    
    for i in range(number_of_runs):
        triage_or_hospital_empty_ratio_mean += triage_or_hospital_empty_ratio_list[i]/number_of_runs
        triage_and_hospital_empty_ratio_mean += triage_and_hospital_empty_ratio_list[i]/number_of_runs
        critical_going_home_ratio_mean += critical_going_home_ratio_list[i]/number_of_runs
        average_nurse_utilization_mean += average_nurse_utilization_list[i]/number_of_runs
        average_occupied_bed_mean += average_occupied_bed_list[i]/number_of_runs
        patient_going_home_ratio_mean += patient_going_home_ratio_list[i]/number_of_runs
        average_healing_time_mean += average_healing_time_list[i]/number_of_runs
        
    # Now we will calculate S values.
        
    for i in range(number_of_runs):
        triage_or_hospital_empty_ratio_variance += (triage_or_hospital_empty_ratio_mean - triage_or_hospital_empty_ratio_list[i])**2 / (number_of_runs-1)
        triage_and_hospital_empty_ratio_variance += (triage_and_hospital_empty_ratio_mean - triage_and_hospital_empty_ratio_list[i])**2 / (number_of_runs-1)
        critical_going_home_ratio_variance += (critical_going_home_ratio_mean - critical_going_home_ratio_list[i])**2 / (number_of_runs-1)
        average_nurse_utilization_variance += (average_nurse_utilization_mean - average_nurse_utilization_list[i])**2 / (number_of_runs-1)
        average_occupied_bed_variance += (average_occupied_bed_mean - average_occupied_bed_list[i])**2 / (number_of_runs-1)
        patient_going_home_ratio_variance += (patient_going_home_ratio_mean -  patient_going_home_ratio_list[i])**2 / (number_of_runs-1)
        average_healing_time_variance += (average_healing_time_mean - average_healing_time_list[i])**2 / (number_of_runs-1)
    
    triage_or_hospital_empty_ratio_variance = math.sqrt(triage_or_hospital_empty_ratio_variance)
    triage_and_hospital_empty_ratio_variance = math.sqrt(triage_and_hospital_empty_ratio_variance)
    critical_going_home_ratio_variance = math.sqrt(critical_going_home_ratio_variance)
    average_nurse_utilization_variance = math.sqrt(average_nurse_utilization_variance)
    average_occupied_bed_variance = math.sqrt(average_occupied_bed_variance)
    patient_going_home_ratio_variance = math.sqrt(patient_going_home_ratio_variance)
    average_healing_time_variance = math.sqrt(average_healing_time_variance)
    
    # Now we will calculate the confidence intervals. We will approximate T distibutions with normal distribution.
    z_value = numpy.random.normal((1-confidence_level)/2) # To not calculate to same value over and over again
    
    triage_or_hospital_empty_ratio_interval[0] = triage_or_hospital_empty_ratio_mean - z_value*(triage_or_hospital_empty_ratio_variance/math.sqrt(number_of_runs))
    triage_or_hospital_empty_ratio_interval[1] = triage_or_hospital_empty_ratio_mean + z_value*(triage_or_hospital_empty_ratio_variance/math.sqrt(number_of_runs))
    
    triage_and_hospital_empty_ratio_interval[0] =  triage_and_hospital_empty_ratio_mean - z_value*(triage_and_hospital_empty_ratio_variance/math.sqrt(number_of_runs))
    triage_and_hospital_empty_ratio_interval[1] = triage_and_hospital_empty_ratio_mean + z_value*(triage_and_hospital_empty_ratio_variance/math.sqrt(number_of_runs))
    
    critical_going_home_ratio_interval[0] = critical_going_home_ratio_mean - z_value*(critical_going_home_ratio_variance/math.sqrt(number_of_runs))
    critical_going_home_ratio_interval[1] = critical_going_home_ratio_mean + z_value*(critical_going_home_ratio_variance/math.sqrt(number_of_runs))
    
    average_nurse_utilization_interval[0] = average_nurse_utilization_mean - z_value*(average_nurse_utilization_variance/math.sqrt(number_of_runs))
    average_nurse_utilization_interval[1] = average_nurse_utilization_mean + z_value*(average_nurse_utilization_variance/math.sqrt(number_of_runs))
    
    average_occupied_bed_interval[0] = average_occupied_bed_mean - z_value*(average_occupied_bed_variance/math.sqrt(number_of_runs))
    average_occupied_bed_interval[1] = average_occupied_bed_mean + z_value*(average_occupied_bed_variance/math.sqrt(number_of_runs))
    
    patient_going_home_ratio_interval[0] = patient_going_home_ratio_mean - z_value*(patient_going_home_ratio_variance/math.sqrt(number_of_runs))
    patient_going_home_ratio_interval[1] = patient_going_home_ratio_mean + z_value*(patient_going_home_ratio_variance/math.sqrt(number_of_runs))
    
    average_healing_time_interval[0] = average_healing_time_mean - z_value*(average_healing_time_variance/math.sqrt(number_of_runs))
    average_healing_time_interval[1] = average_healing_time_mean + z_value*(average_healing_time_variance/math.sqrt(number_of_runs))
    
    print("Results after",number_of_runs,"runs:")
    print("mean triage or hospital empty ratio:",triage_or_hospital_empty_ratio_mean)
    print("mean triage and hospital empty ratio:",triage_and_hospital_empty_ratio_mean)
    print("mean critical going home ratio:",critical_going_home_ratio_mean)
    print("mean average nurse utilization:",average_nurse_utilization_mean)
    print("mean average occupied bed:",average_occupied_bed_mean)
    print("mean patient going home ratio:",patient_going_home_ratio_mean)
    print("mean average healing time:",average_healing_time_mean)
    print("---")
    print("triage or hospital empty ratio variance:",triage_or_hospital_empty_ratio_variance)
    print("triage and hospital empty ratio variance:",triage_and_hospital_empty_ratio_variance)
    print("critical going home ratio variance:",critical_going_home_ratio_variance)
    print("average nurse utilization variance:",average_nurse_utilization_variance)
    print("average occupied bed variance:",average_occupied_bed_variance)
    print("patient going home ratio variance:",patient_going_home_ratio_variance)
    print("average healing time variance:",average_healing_time_variance)
    print("------------------")
    # To calculate the interval we should use T disribution . But we can approximate by using the normal distibution.
    print(f"The confidence intervals with %{int(confidence_level*100)} condifence level:")
    print(f"triage or hospital empty ratio interval: [{triage_or_hospital_empty_ratio_interval[0]},{triage_or_hospital_empty_ratio_interval[1]}]")
    print(f"triage and hospital empty ratio interval: [{triage_and_hospital_empty_ratio_interval[0]},{triage_and_hospital_empty_ratio_interval[1]}]")
    print(f"critical going home ratio interval: [{critical_going_home_ratio_interval[0]},{critical_going_home_ratio_interval[1]}]")
    print(f"average nurse utilization interval: [{average_nurse_utilization_interval[0]},{average_nurse_utilization_interval[1]}]")
    print(f"average occupied bed interval: [{average_occupied_bed_interval[0]},{average_occupied_bed_interval[1]}]")
    print(f"patient going home ratio interval: [{patient_going_home_ratio_interval[0]},{patient_going_home_ratio_interval[1]}]")
    print(f"average healing time interval: [{average_healing_time_interval[0]},{average_healing_time_interval[1]}]")
    
       
    
    
