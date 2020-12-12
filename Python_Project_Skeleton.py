import numpy as np
def fade():             #Fading
    x = np.random.normal(0,1,10)
    y = np.random.normal(0,1,10)
    z = x + y*(1j)
    a = np.abs(z)
    ans = 20*np.log10(a)
    ans.sort()
    return ans[1]
def Oka_hata(d):          #Path_loss
    d = d/1000
    h_m = 1.7
    h_b = 50
    f = 1000
    a = (1.1*np.log10(f) - 0.7)*h_m - (1.56*np.log10(f) - 0.8)
    temp = 69.55 + 26.16*np.log10(f) - 13.82*np.log10(h_b) + (44.9 - 6.55*np.log10(h_b))*np.log10(d) - a
    return temp
user = int(input("Enter number of users: "))
x = int(input("Enter simulation time in hours: "))
time = (x*60*60)                                        #Time in seconds
speed = int(input("Enter the user's speed in m/s: "))
distance = int(input("Enter the distance between BSTN's in km: "))
distance = distance*1000
users =  [] #[ID,distance,direction,duration,active call,HO_timer,BSTN]
for i in range(0,user):
        users.append([i,0,'direction',0,'No',0,0])
RSL_threshold = -102
hour=1
EIRP = 55
SHAD_RES=10
shad_values = int(distance/SHAD_RES)
HO_TIMER=3
flag=0
channels_1=30
channels_2=30
active_calls_1=[]
active_calls_2=[]
attempt_1=0
attempt_2=0
succ_conn_1=0
succ_conn_2=0
succ_call_1=0
succ_call_2=0
HO_by_1=0
HO_by_2=0
succ_HO_1=0
succ_HO_2=0
HO_fail_1=0
HO_fail_2=0
active_call_drop_1=0
active_call_drop_2=0
call_drop_1=0
call_drop_2=0
capacity_block_1=0
capacity_block_2=0
ss_block_1=0
ss_block_2=0
shadowing_1=np.random.normal(0,2,shad_values)
shadowing_2=np.random.normal(0,2,shad_values)
flag=0
for t in range (1,time+1):                       #Total number of seconds
    for u in users:             #Traversing through the list of users    
        if(u[4]=='Yes'):            #Yes indicating call is up
            if(u[2]=='right'):                       # update location
                u[1] += speed #(m/s)
            else:                                       #going left
                u[1] -= speed #(m/s)                                  
            u[3] -= 1                             #Decrement the duration
            if(u[3]==0 or (u[1]<1 or u[1]>distance-1)):    #Call Success
                if(u[6]==1):                #Successful entry for BSTN 1
                    channels_1 += 1         #Releasing the channel
                    active_calls_1.remove(u[0])
                    succ_call_1 += 1
                    if(u[5]>0 and u[5]<=HO_TIMER+1):  #Whether in between handoff
                        channels_2 += 1
                        active_calls_2.remove(u[0])
                else:                       #Successful entry for BSTN 2
                    channels_2 += 1          #Releasing the channel
                    active_calls_2.remove(u[0])
                    succ_call_2 += 1
                    if(u[5]>0 and u[5]<=HO_TIMER+1):   #Whether in between handoff
                        channels_1 += 1       #Releasing the channel
                        active_calls_1.remove(u[0]) #Remove from active call list
                u[4]='No'      #Change call status to not up
                continue
            path_loss_1 = Oka_hata(u[1])  #Decibels    #Distance from BSTN 1
            index1 = int(u[1]/10)     #Shadowing index for BSTN 1
            index2 = int((distance-u[1])/10)  #Shadowing index for BSTN 1
            shadow_1 = shadowing_1[index1] #Decibels
            path_loss_2 = Oka_hata(distance-u[1])  #Decibels #Dist. from BSTN2
            shadow_2 = shadowing_2[index2] #Decibels
            if(u[6]==1):    #Current serving base station is 1
                RSL_serving = EIRP - path_loss_1 + shadow_1 + fade()
                RSL_other = EIRP - path_loss_2 + shadow_2 + fade()
            else:            #Current serving base station is 2
                RSL_serving = EIRP - path_loss_2 + shadow_2 + fade()
                RSL_other = EIRP - path_loss_1 + shadow_1 + fade()
            if(RSL_serving<RSL_threshold):    #Call Drops
                if(u[6]==1):        #If serving BSTN is 1
                    active_call_drop_1 += 1
                    active_calls_1.remove(u[0])       #Remove from active calls list
                    channels_1 += 1 #Channel released
                    if(u[5]>0 and u[5]<=HO_TIMER+1):
                        channels_2 += 1     #Releasing the channel
                        active_calls_2.remove(u[0])
                        HO_fail_1 += 1
                else:
                    active_call_drop_2 += 1
                    active_calls_2.remove(u[0])
                    channels_2 += 1      #Releasing the channel
                    if(u[5]>0 and u[5]<=HO_TIMER+1):
                        channels_1 += 1    #Releasing the channel
                        active_calls_1.remove(u[0])
                        HO_fail_2 += 1
                u[4]='No'           #Change call status to not up
                continue
            else:
                if(RSL_other>RSL_serving):     #Handoff is triggered
                    if(u[5]==0):
                        if(u[6]==1):
                            HO_by_1 += 1
                            if(channels_2>0):
                                channels_2 -= 1
                                active_calls_2.append(u[0])
                                u[5] += 1
                            else:
                                HO_fail_1 += 1
                                capacity_block_2 += 1
                        else:
                            HO_by_2 += 1
                            if(channels_1>0):
                                channels_1 -= 1
                                active_calls_1.append(u[0])
                                u[5] += 1
                            else:
                                HO_fail_2 += 1
                                capacity_block_1 += 1
                    elif(u[5]>0 and u[5]<=HO_TIMER):  #Handoff in progress
                        u[5] += 1       #Increment Handoff counter
                        continue
                    else:              #Handoff Successful
                        u[5]=0          #Reset Timer
                        if(u[6]==1):
                            u[6]=2    #Change serving base station from 1 to 2
                            succ_HO_1 += 1
                            channels_1 += 1  #Release channel
                            active_calls_1.remove(u[0])
                        else:
                            u[6]=1
                            succ_HO_2 += 1
                            channels_2 += 1
                            active_calls_2.remove(u[0])
                        continue
                else:                       #Continue with same bstn
                    continue
        else:                            #User doesn't have an active call
            
             x = np.random.uniform(0,3600)   #Probability that a user makes a call
             if(x<1):                     #User makes a call
                 u[1]=np.random.uniform(0,distance)   #Random distribution
                 if(u[1]<(distance/2)):     #Determining direction
                     u[2]='right'
                 else:
                     u[2]='left'
                 u[3]=0        #Call Duration reset
                 u[5]=0        #Handoff timer reset
                 u[6]=0        #Current serving BSTN none or 0
                 path_loss_1 = Oka_hata(u[1])
                 path_loss_2 = Oka_hata(distance-u[1])
                 index1 = int(u[1]/10)
                 index2 = int((distance-u[1])/10)
                 shadow_1 = shadowing_1[index1]
                 shadow_2 = shadowing_2[index2]
                 RSL_1 = EIRP - path_loss_1 + shadow_1 + fade()
                 RSL_2 = EIRP - path_loss_2 + shadow_2 + fade()
                 if(RSL_1>=RSL_2):      #BSTN 1 dominant
                     if(RSL_1>=RSL_threshold):        
                         attempt_1 += 1   #Attempts a call
                         if(channels_1>0):             #Channel available
                             u[3]=int(np.random.exponential(180)) #Duration
                             u[4]='Yes'            #Call is active
                             u[6]=1                  #BSTN_Serving
                             channels_1 -= 1         #Allocate the channel
                             succ_conn_1 += 1
                             active_calls_1.append(u[0])  #Make an entry for user
                             continue
                         else:                      #Channel not available
                             capacity_block_1 += 1    #Block due to capacity
                             if(RSL_2>=RSL_threshold):    #Helper
                                 attempt_2 += 1
                                 if(channels_2>0):
                                     u[3]=int(np.random.exponential(180)) #Duration
                                     u[4]='Yes'    #Call is active
                                     u[6]=2                  #BSTN_Serving
                                     channels_2 -= 1        #Allocate the channel
                                     succ_conn_2 += 1
                                     active_calls_2.append(u[0])  #Make an entry for user
                                     continue
                                 else:            #Drop for 1st BSTN
                                     call_drop_1 += 1
                                     continue
                             else:                 #Drop for 1st BSTN
                                call_drop_1 += 1
                                continue
                     else:
                         ss_block_1 += 1
                         continue
                 else:                             #BSTN2>BSTN1
                     if(RSL_2>=RSL_threshold):
                         attempt_2 += 1
                         if(channels_2>0):             #Channel available
                             u[3]=int(np.random.exponential(180)) #Duration
                             u[4]='Yes'            #Call is active
                             u[6]=2                  #BSTN_Serving
                             channels_2 -= 1        #Allocate the channel
                             succ_conn_2 += 1
                             active_calls_2.append(u[0])  #Make an entry for user
                             continue
                         else:                      #Channel not available
                             capacity_block_2 += 1    #Block due to capacity
                             if(RSL_1>=RSL_threshold):    #Helper
                                 attempt_1 += 1
                                 if(channels_1>0):
                                     u[3]=int(np.random.exponential(180)) #Duration
                                     u[4]='Yes'    #Call is active
                                     u[6]=1                  #BSTN_Serving
                                     channels_1 -= 1        #Allocate the channel
                                     succ_conn_1 += 1
                                     active_calls_1.append(u[0])  #Make an entry for user
                                     continue
                                 else:            #Drop for BSTN 2
                                     call_drop_2 += 1
                                     continue
                             else:                 #Drop for BSTN 2
                                call_drop_2 += 1
                                continue
                     else:
                         ss_block_2 += 1
                         continue

             else:
                 #User doesn't make a call
                 continue
    if(t%3600==0):
        if(t==time):
            flag=1
        if(flag==0):
            print("After {0} hour".format(hour))
        else:
            print("End of simulation summary report")
        hour += 1
        print("For Base station 1")
        print("Channels in use : {0}".format(30-channels_1))
        print("Available channels : {0}".format(channels_1))
        print("Number of currently active calls : {0}".format(len(active_calls_1)))
        print("Number of calls attempted : {0}".format(attempt_1))
        print("Number of successful connections : {0}".format(succ_conn_1))
        print("Number of successful calls : {0}".format(succ_call_1))
        print("Handoffs attempted : {0}".format(HO_by_1))
        print("Handoffs successfully completed : {0}".format(succ_HO_1))
        print("Failed Handoffs : {0}".format(HO_fail_1))
        print("Call dropped or finished in between handoff : {0}".format(HO_by_1-succ_HO_1-HO_fail_1))
        print("Number of active call drops : {0}".format(active_call_drop_1))
        print("Calls dropped : {0}".format(call_drop_1 + active_call_drop_1))
        print("Calls blocked because of lack of channels : {0}".format(capacity_block_1))
        print("Calls blocked because of signal strength : {0}".format(ss_block_1))
        print()
        print("For Base station 2")
        print("Channels in use : {0}".format(30-channels_2))
        print("Available channels : {0}".format(channels_2))
        print("Number of currently active calls : {0}".format(len(active_calls_2)))
        print("Number of calls attempted : {0}".format(attempt_2))
        print("Number of successful connections : {0}".format(succ_conn_2))
        print("Number of successful calls : {0}".format(succ_call_2))
        print("Handoffs attempted : {0}".format(HO_by_2))
        print("Handoffs successfully completed : {0}".format(succ_HO_2))
        print("Failed Handoffs : {0}".format(HO_fail_2))
        print("Call dropped or finished in between handoff : {0}".format(HO_by_2-succ_HO_2-HO_fail_2))
        print("Number of active call drops : {0}".format(active_call_drop_2))
        print("Calls dropped : {0}".format(call_drop_2 + active_call_drop_2))
        print("Calls blocked because of lack of channels : {0}".format(capacity_block_2))
        print("Calls blocked because of signal strength : {0}".format(ss_block_2))
        print()