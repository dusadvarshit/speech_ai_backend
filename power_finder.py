'''Import necessary libraries'''
'''Make the necessary imports'''
import os
import numpy as np
from numpy import mean
import random
from math import ceil, floor
import json
from scipy.signal import hamming 
import pandas as pd
import numpy as np
import sys
import parselmouth
from scipy.io import wavfile
from scipy.signal import medfilt
import math
from parselmouth.praat import call

def energy_feedback(energy_score):
    
    text = ''
    text_list = []
    if energy_score>=90:
        temp_lst = ['Great job!', 'Great work!', 'Excellent!', 'Bravo!', 'Amazing work!', 'Exemplary work!', 
                   ]
        temp_lst2 = ["Your energy is commendable.', 'Your voice carries energy and momentum that can catch people's attention .",
                    'Your power reflects the confidence you have in yourself and your preparation',
                    'Your energy is high and that is a good note to start a speech on.']
        random.shuffle(temp_lst)
        random.shuffle(temp_lst2)
        text += """{} {}. While a good energy is nice to have, being too loud will also turn off your audience. It is best to start with strong energy and then bring variation along with vocal variety. It would be best to start with high energy, then maintain a consistent, normal volume and soften up if the speech demands it such as when showing despair and grief.""".format(temp_lst[0], temp_lst2[0])
        text_list += [temp_lst[0], temp_lst2[0], """While a good energy is nice to have, being too loud will also turn off your audience. It is best to start with strong energy and then bring variation along with vocal variety. It would be best to start with high energy, then maintain a consistent, normal volume and soften up if the speech demands it such as when showing despair and grief."""]
    
    elif energy_score>=60:
        temp_lst = ['Good job!', 'Good work!', 'Well done!', 'Nice!']
        temp_lst2 = ['You are doing well but can still improve your overall energy.', 
                     'Your speaking voice is commanding but there is room for further improvement.',
                    "You can attract people's attention but with further practice you will be able to hold it for longer duration.",
                    "Your speaking voice has potential but with further practice it can be perfected for even live auditorium."]
        random.shuffle(temp_lst)
        random.shuffle(temp_lst2)
        text += """{} {}. Having a good power is a great way to start a speech as it catches audience attention and create a positive, energetic vibe. You can improve your energy by practicing taking long breaths and speaking out sounds such as Om, Do, Re, Me, Fa, So, La, Ti for extended periods of time.""".format(temp_lst[0], temp_lst2[0])
        text_list += [temp_lst[0], temp_lst2[0], """Having a good power is a great way to start a speech as it catches audience attention and create a positive, energetic vibe. You can improve your energy by practicing taking long breaths and speaking out sounds such as Om, Do, Re, Me, Fa, So, La, Ti for extended periods of time."""]
        
    elif energy_score<60:
        temp_lst = ['Satisfactory!', 'OK!', 'Not great!', 'You can do better!']
        temp_lst2 = ['Your needs further improvement as you would not be audible to many people.', 
                     "Your speech lacks the gravity to catch people's attention.",
                    'You should work more on to increasing the strength of throat muscle to improve your vocal strength.',
                    'Your voice is too soft and uninspiring at the moment.']
        random.shuffle(temp_lst)
        random.shuffle(temp_lst2)
        text += """{} {}. Speaking with energy is vital for audience engagement. A lot of power comes from your lungs and breathing. Try practicing breathing and speaking from your stomach which means always take deep breath to fill all your diaphragm. Beyond that speak out loud sounds such as Om, Do, Re, Me, Fa, So, La, Ti for extended periods of time.""".format(temp_lst[0], temp_lst2[0])
        text_list += [temp_lst[0], temp_lst2[0], """Speaking with energy is vital for audience engagement. A lot of power comes from your lungs and breathing. Try practicing breathing and speaking from your stomach which means always take deep breath to fill all your diaphragm. Beyond that speak out loud sounds such as Om, Do, Re, Me, Fa, So, La, Ti for extended periods of time."""]
        
    return text, text_list

def return_energy_score(file_location):

    snd = parselmouth.Sound(file_location)
    intensity = snd.to_intensity()
    item = intensity.values.T
    
    new_item = []
    for val in item:
        if (val>=50) and (val<=75):
            new_item.append(1)
        elif (val<50) and (val>=30):
            new_item.append(-1)
        elif val>75:
            new_item.append(2)
        else:
            new_item.append(0)
    
    energy_score = sum([i for i in new_item if i!=0])/(len([i for i in new_item if i!=0]))*100
    
    return energy_score

