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


def return_pitch_score(file_location):

    snd = parselmouth.Sound(file_location)
    pitch = snd.to_pitch()
    pitch = pitch.selected_array['frequency']
    
    new_item = []
    for val in pitch:
        if (val>=200) and (val<=300):
            new_item.append(1)
        elif val<200:
            new_item.append(0)
        else:
            new_item.append(2)
            
    pitch_score =  sum(new_item)/(len(new_item))*100
    
    return pitch_score

def pitch_feedback(pitch_score):
    
    text = ''
    text_list = []
    if pitch_score>=90:
        temp_lst = ['Great job!', 'Great work!', 'Excellent!', 'Bravo!', 'Amazing work!', 'Exemplary work!', 
                   ]
        temp_lst2 = ['Your use of vocal variety is commendable.', 'Your intonation and emphasis is adding beauty to your speech.',
                    'Your vocal variety will make listener want to listen to you.',
                    'Your pitch variation helps in expanding the meaning behind your words.']
        random.shuffle(temp_lst)
        random.shuffle(temp_lst2)
        text += """{} {} Afterall, a good vocal variety helps in communicating clear message to your audience about your intention. This makes you more memorable as a speaker and makes it easy to follow the key message you are trying to emphasize. However, beware of too much vocal variation as that will appear phony and pretentious.""".format(temp_lst[0], temp_lst2[0])
        text_list += [temp_lst[0], temp_lst2[0], """Afterall, a good vocal variety helps in communicating clear message to your audience about your intention. This makes you more memorable as a speaker and makes it easy to follow the key message you are trying to emphasize. However, beware of too much vocal variation as that will appear phony and pretentious."""]
    
    elif pitch_score>=60:
        temp_lst = ['Good job!', 'Good work!', 'Well done!', 'Nice!']
        temp_lst2 = ['You are doing well but can improve your vocal variation.', 
                     'Your speech intonation is good because you are able to modify the pitch of your voice. Nonetheless, you can do better.',
                    'Your vocal variation deserves praise, but work on bringing more emotions into your speech to make it better.',
                    'Your speech can illustrate your emotions and thus meaning behind your words. However, record yourself and listen to improve your vocal variation even more.']
        random.shuffle(temp_lst)
        random.shuffle(temp_lst2)
        text += """{} {}. The level of vocal variety you can bring to your speech adds more life into your speech. It not only helps to illustrate your meaning better but also improves your overall tone which makes it pleasant for audience to listen to you.""".format(temp_lst[0], temp_lst2[0])
        text_list += [temp_lst[0], temp_lst2[0], """The level of vocal variety you can bring to your speech adds more life into your speech. It not only helps to illustrate your meaning better but also improves your overall tone which makes it pleasant for audience to listen to you."""]
        
    elif pitch_score<60:
        temp_lst = ['Satisfactory!', 'OK!', 'Not great!', 'You can do better!']
        temp_lst2 = ['You need to improve your vocal variation.', 
                     'Your speech yet lacks the variation and appeal to excite the audience to listen to you.',
                    'You should work more on to infusing emotions into your words to make it more exciting and less monotonous.',
                    'Your speaking style yet is quite montonous. Try practicing elongating your vowels and also try to infuse more emotions into your words.']
        random.shuffle(temp_lst)
        random.shuffle(temp_lst2)
        text += """{} {}. Having poor vocal range signifies lack of emotion and excitement in a speech. This can bore audience and lose them to stop listening. A good way to improve vocal variety is to practice your favorite movie dialogues especially which are emotional like patriotic movies. This will start to build your natural tendency to bring different flavors in your speech.""".format(temp_lst[0], temp_lst2[0])
        text_list += [temp_lst[0], temp_lst2[0], """Having poor vocal range signifies lack of emotion and excitement in a speech. This can bore audience and lose them to stop listening. A good way to improve vocal variety is to practice your favorite movie dialogues especially which are emotional like patriotic movies. This will start to build your natural tendency to bring different flavors in your speech."""]
        
    return text, text_list