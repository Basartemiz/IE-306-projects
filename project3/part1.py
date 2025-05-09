import simpy
import random
import matplotlib.pyplot as plt

#-------variables---------
INTERARRIVAL_RATE =76 
N_OPERATOR=2
service_rate=40 #to be adjusted
repetition_count=10


all_soujourn_times=[]

#-------variables-----------


#-----functions--------------
def getService(env,operator,soujourn_times):

    with operator.request() as req: #try to get request

        arrival_time=env.now #just arrived to the system

        yield req #try to get the service

        yield env.process(serviceCostumer(env))

        leave_time=env.now #just left to the system
        soujourn_times.append(leave_time-arrival_time)

       

    

def serviceCostumer(env): 
    service_duration = random.expovariate(service_rate)
    yield env.timeout(service_duration)


def generateInterArrival(env, operator,soujourn_times):
    """Generate new cars that arrive at the gas station."""
    for i in range(10000):
        yield env.timeout(random.expovariate(INTERARRIVAL_RATE))
        env.process(getService(env,operator,soujourn_times))
#-----functions--------------




for i in range (repetition_count):

    #set random seed
    random_seed=43
    random.seed(random_seed+i)  # Set the seed


    # simulation setup
    env = simpy.Environment() #creating environment

    operator = simpy.Resource(env,N_OPERATOR) #creating service operators

    soujourn_times=[] #create soujourn times array

    env.process(generateInterArrival(env, operator,soujourn_times)) #start the process

    env.run() #start the environments

    all_soujourn_times.append(soujourn_times)

#------plot-----------
average_L=0
plt.figure(figsize=(12, 6))
for i, soujourns in enumerate(all_soujourn_times):
    average_L=(average_L*(i)+sum(soujourn_times)/len(soujourn_times))/(i+1)
    plt.plot(soujourns, label=f'Repetition {i+1}')

plt.xlabel("costumer count")
plt.ylabel("Sojourn Time")
plt.title(f"Sojourn Times Across Repetitions server usage 50 percent with L as {average_L}")
plt.legend()
plt.grid(True)
plt.show()
#------plot-----------
    
#------plot repetition 1 only-----------
plt.figure(figsize=(10, 5))
plt.plot(all_soujourn_times[0], label="Repetition 1", color='blue')

plt.xlabel("Customer index")
plt.ylabel("Sojourn Time")
plt.title("Sojourn Time for Repetition 1 Only")
plt.legend()
plt.grid(True)
plt.show()
#------plot repetition 1 only-----------