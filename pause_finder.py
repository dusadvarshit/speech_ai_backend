'''Import necessary libraries'''
'''Make the necessary imports'''
import os
import numpy as np
from numpy import mean
import random
from math import ceil, floor
import json
from scipy.signal import hamming 
import numpy as np
import sys
import parselmouth
from scipy.io import wavfile
from scipy.signal import medfilt
import math
from parselmouth.praat import call

# Compute the short-term energy and spectral centroid of the signal
def ShortTimeEnergy(signal, windowLength,step):
    signal = signal / max(signal)
    curPos = 1;
    L = len(signal)
    
    from math import floor, ceil
    numOfFrames = floor((L-windowLength)/step) + 1;
    
    E = np.zeros((numOfFrames,1))
    
    for i in range(numOfFrames):
        window = signal[ceil(curPos):ceil(curPos+ windowLength-1)];
        E[i] = (1/(windowLength)) * sum(abs(np.power(window,2)));
        curPos = curPos + step;
        
    return E

# Compute the short-term energy and spectral centroid of the signal
def SpectralCentroid(signal, windowLength, step, fs):
    windowLength = ceil(windowLength);
    
    signal = signal / max(abs(signal));
    
    curPos = 0;
    L = len(signal);
    numOfFrames = floor((L-windowLength)/step) + 1;
    
    H = hamming(windowLength);
    m = np.array([(fs/(2*windowLength))*float(i+1) for i in range(windowLength)])
    m = m.transpose()
    C = np.zeros((numOfFrames,1))
    
    for i in range(numOfFrames):

        # Broadcast length check
        broadcast_length = len(signal[ceil(curPos):ceil(curPos+windowLength)])

        window = H[0:broadcast_length]*signal[ceil(curPos):ceil(curPos+windowLength)]
        FFT = (abs(np.fft.fft(window,2*windowLength)));
        FFT = FFT[0:windowLength];  
        FFT = FFT / max(FFT);
        C[i] = sum(m*FFT)/sum(FFT);
        if (sum(np.power(window,2))<0.010):
            C[i] = 0.0

        curPos = curPos + step;
        
    C = C / (fs/2);
    
    return C

def findMaxima(f, step):
    
    countMaxima = 0

    Maxima = [[], []]

    for i in range(0, len(f)-step-1):  # for each element of the sequence:
        if (i>step):
            if (( mean(f[i-step:i])< f[i]) and ( mean(f[i+1:i+step+1])< f[i])):  
                # IF the current element is larger than its neighbors (2*step window)
                # --> keep maximum:
                countMaxima = countMaxima + 1;
                Maxima[0].append(i);
                Maxima[1].append(f[i]);
        else:
            if (( mean(f[0:i+1])<= f[i]) and ( mean(f[i+1:i+step])< f[i])):
                # IF the current element is larger than its neighbors (2*step window)~
                # --> keep maximum:
                countMaxima = countMaxima + 1;
                Maxima[0].append(i);
                Maxima[1].append(f[i]);
                

    #
    # STEP 2: post process maxima:
    #

    MaximaNew = [[], []];
    countNewMaxima = 0;
    i = 0; # Python indexing starts from 0
    while (i<countMaxima-1):
        # get current maximum:

        curMaxima = Maxima[0][i];
        curMavVal = Maxima[1][i];

        tempMax = [Maxima[0][i]];
        tempVals = [Maxima[1][i]];

        # search for "neighbourh maxima":
        while ((i<countMaxima-1) and ( Maxima[0][i+1] - tempMax[-1] < step / 2)):
            tempMax.append(Maxima[0][i]);
            tempVals.append(Maxima[1][i]);
            i = i + 1;

        # find the maximum value and index from the tempVals array:
        # MI = findCentroid(tempMax, tempVals); MM = tempVals(MI);

        MM = max(tempVals);
        MI = np.argmax(tempVals);

        if (MM>0.02*mean(f)): # if the current maximum is "large" enough:
            # keep the maximum of all maxima in the region:
            MaximaNew[0].append(tempMax[MI]) 
            MaximaNew[1].append(f[MaximaNew[0][countNewMaxima]]);

            countNewMaxima = countNewMaxima + 1;   # add maxima

        tempMax = [];
        tempVals = [];

        ## Update the counter
        i = i + 1;

    Maxima = MaximaNew;
    countMaxima = countNewMaxima;   
    
    return (Maxima, countMaxima)

def pause_score(pause_info, time_arr):
    short_pauses = [(i['pause_start'], i['pause_finish'], i['pause_duration']) for i in pause_info if (i['pause_duration']>=0.5 and i['pause_duration']<1)]
    long_pauses = [(i['pause_start'], i['pause_finish'], i['pause_duration']) for i in pause_info if (i['pause_duration']>=1)]

    pause_score = np.round(((1 - sum([i['pause_duration'] for i in pause_info])/time_arr[-1]))*100)

    print(short_pauses)
    print(long_pauses)
    
    if len(short_pauses)<=1 and len(long_pauses)<=1:
        print('You took {} short pause and {} long pause.'.format(len(short_pauses), len(long_pauses)))
    elif len(short_pauses)<=1:
        print('You took {} short pause and {} long pauses.'.format(len(short_pauses), len(long_pauses)))
    elif len(long_pauses)<=1:
        print('You took {} short pauses and {} long pause.'.format(len(short_pauses), len(long_pauses)))
    else:
        print('You took {} short pauses and {} long pauses.'.format(len(short_pauses), len(long_pauses)))
        
    text = pause_feedback(pause_score)
        
    return pause_score, text  


def pause_feedback(pause_score):
    
    text = ''
    text_list = []
    if pause_score>=90:
        temp_lst = ['Great job!', 'Great work!', 'Excellent!', 'Bravo!', 'Amazing work!', 'Exemplary work!', 
                   ]
        temp_lst2 = ['You are doing well in reducing awkward pauses.', 'The less awkward pauses you have, the better your speech.',
                    'With fewer awkward pauses the flow of your speech is not broken and its easy to understand.',
                    'You really prepared your speech well as visible by your lack of awkward pauses.']
        random.shuffle(temp_lst)
        random.shuffle(temp_lst2)
        text += """{} {} But remember pauses are not all bad. Great speakers use pause for introducing dramatic effect and introduce smooth transitions between their speech. Just imagine an anchor on stage saying, "Please, welcome the one and only.... Amitabh Bachhan." You will notice that there is often a pause before introducing Amitabh Bachhan in order to create suspense. Now you too practice introducing pauses purposefully to increase the quality of your speech.""".format(temp_lst[0], temp_lst2[0])
        text_list += [temp_lst[0], temp_lst2[0], """But remember pauses are not all bad. Great speakers use pause for introducing dramatic effect and introduce smooth transitions between their speech. Just imagine an anchor on stage saying, "Please, welcome the one and only.... Amitabh Bachhan." You will notice that there is often a pause before introducing Amitabh Bachhan in order to create suspense. Now you too practice introducing pauses purposefully to increase the quality of your speech."""]
    
    elif pause_score>=80:
        temp_lst = ['Good job!', 'Good work!', 'Well done!', 'Nice!']
        temp_lst2 = ['You are doing well but can improve in reducing awkward pauses.', 
                     'Your speech flow is good because you lack large number of awkward pauses. Nonetheless, you can do better.',
                    'You are on path of success, work even more to reduce the number of clumsy pauses in your speech.',
                    'Work on your speech some more until you minimize the number of unexpected pauses you take.']
        random.shuffle(temp_lst)
        random.shuffle(temp_lst2)
        text += """{} {} When you have unexpected pauses then it can distract your audience. A pause can be powerful if it is planned well in speech such as an introduction (Here comes Mr. Akshay), or an exclamation (Wow!). However, unplanned pauses breaks your sentences in between and confuses your audience.""".format(temp_lst[0], temp_lst2[0])
        text_list += [temp_lst[0], temp_lst2[0], """When you have unexpected pauses then it can distract your audience. A pause can be powerful if it is planned well in speech such as an introduction (Here comes Mr. Akshay), or an exclamation (Wow!). However, unplanned pauses breaks your sentences in between and confuses your audience."""]
        
    elif pause_score<80:
        temp_lst = ['Satisfactory!', 'OK!', 'Not great!', 'You can do better!']
        temp_lst2 = ['You need to improve in reducing clumsy pauses.', 
                     'You have unusually large number of unexpected pauses in your speech.',
                    'You should work more to reduce the number of long and short pauses from your speech.',
                    'Your quality of speech can be improved by reducing the number of these awkward pauses.']
        random.shuffle(temp_lst)
        random.shuffle(temp_lst2)
        text += """{} {} A large number of pauses in a speech is a sign of either lack of confidence or lack of preparation. Sometimes both. Try to practice your speech in advance in front of mirror or members of your family without any notes to improve confidence. Having less unwanted pauses will make you appear more confident in front of your audience and will also make you easy to understand.""".format(temp_lst[0], temp_lst2[0])
        text_list += [temp_lst[0], temp_lst2[0], """A large number of pauses in a speech is a sign of either lack of confidence or lack of preparation. Sometimes both. Try to practice your speech in advance in front of mirror or members of your family without any notes to improve confidence. Having less unwanted pauses will make you appear more confident in front of your audience and will also make you easy to understand."""]
        
    return text


'''Main function call'''
def pause_main(file_location):

    '''Read the file'''
    fs, x = wavfile.read(file_location)
    if len(x.shape)>1:  
        if x.shape[1] > 1:
            x = np.mean(x, axis=1)

    N = len(x)
    t = [i/fs for i in range(N)]; # Transform into time domain


    # Window length and step (in seconds)
    win = 0.050
    step = 0.050

    ## Threshold Estimation
    Weight = 5 # Used in the threshold estimation method

    Eor = ShortTimeEnergy(x, win*fs, step*fs)
    # Compute spectral centroid
    Cor = SpectralCentroid(x, win*fs, step*fs, fs)

    # Apply median filtering in the feature sequences (twice), using 5 windows:
    # (i.e., 250 mseconds)
    E = medfilt(medfilt([i[0] for i in Eor.tolist()], 5), 5)

    C = medfilt(medfilt([i[0] for i in Cor.tolist()], 5), 5)

    # Get the average values of the smoothed feature sequences:
    E_mean = np.mean(E);
    Z_mean = np.mean(C);

    # Find energy threshold
    [HistE, X_E] = np.histogram(E, bins = round(len(E) / 10));  # histogram computation
    X_E = np.array([(X_E[idx]+X_E[idx+1])/2 for idx in range(len(X_E)-1)])

    [MaximaE, countMaximaE] = findMaxima(HistE, 3);

    if (len(MaximaE[0])>=2): # if at least two local maxima have been found in the histogram:
        T_E = (Weight*X_E[MaximaE[0][0]]+X_E[MaximaE[0][1]]) / (Weight+1); # ... then compute the threshold as the weighted average between the two first histogram's local maxima.
    else:
        T_E = E_mean / 2;

    # Find spectral centroid threshold:
    [HistC, X_C] = np.histogram(C, round(len(C) / 10));
    X_C = np.array([(X_C[idx]+X_C[idx+1])/2 for idx in range(len(X_C)-1)])

    [MaximaC, countMaximaC] = findMaxima(HistC, 3);
    if (len(MaximaC[0])>=2):
        T_C = (Weight*X_C[MaximaC[0][0]]+X_C[MaximaC[0][1]]) / (Weight+1);
    else:
        T_C = Z_mean / 2;

    Flags1 = (E>=T_E);
    Flags2 = (C>=T_C);
    
    '''Check if array broadcasting doesn't have issues.'''
    if Flags1.shape[0]!=Flags2.shape[0]:
        if Flags1.shape[0]>Flags2.shape[0]:
            Flags1 = Flags1[0:Flags2.shape[0]]

        if Flags2.shape[0]>Flags1.shape[0]:
            Flags2 = Flags1[0:Flags1.shape[0]]
        
    flags = Flags1 & Flags2

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %  SPEECH SEGMENTS DETECTION
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    count = 0;
    WIN = 5;
    Limits = [[], []];
    while (count < len(flags)): # while there are windows to be processed:
        # initilize:
        curX = [];
        countTemp = 1;
        # while flags=1:
        while ((flags[count]==True) and (count < len(flags))):
            if (countTemp==1): # if this is the first of the current speech segment:
                Limit1 = round((count+1-WIN)*step*fs)+1; # set start limit:
                if (Limit1<1):
                    Limit1 = 1;         

            count = count + 1; # increase overall counter
            
            if count==len(flags):
                break
            
            countTemp = countTemp + 1; # increase counter of the CURRENT speech segment

        if (countTemp>1): # if at least one segment has been found in the current loop:
            Limit2 = round((count+1+WIN)*step*fs); # set end counter
            if (Limit2>len(x)):
                Limit2 = len(x);

            Limits[0].append(Limit1-1);
            Limits[1].append(Limit2-1);

        count = count + 1; # increase overall counter

    # %%%%%%%%%%%%%%%%%%%%%%%
    # % POST - PROCESS      %
    # %%%%%%%%%%%%%%%%%%%%%%%
    # % A. MERGE OVERLAPPING SEGMENTS:
    RUN = 1;
    while RUN==1:
        RUN = 0;
        for i in range(0, len(Limits[0])-1): # for each segment
            if (Limits[1][i]>=Limits[0][i+1]):
                RUN = 1;
                Limits[1][i] = Limits[1][i+1];
                Limits[0].pop(i+1)
                Limits[1].pop(i+1)
                break

    # B. Get final segments:
    segments = [];
    for i in range(0, len(Limits[0])):
        segments.append(x[Limits[0][i]:Limits[1][i]]); 

    # Record pause positions
    pause_positions = [[0 for i in range(len(Limits[0]))], [0 for i in range(len(Limits[0]))]]

    for i in range(0, len(segments)): # Number of segments = Number of Limits
        if i==0:
            if Limits[0][0]!=0:
                pause_positions[0][0] = 0;
                pause_positions[1][0] = Limits[0][0];
            else:
                pause_positions[0][0] = Limits[0][0];
                pause_positions[1][0] = Limits[1][0];

        else:
            pause_positions[0][i] = Limits[1][i-1];
            pause_positions[1][i] = Limits[0][i];

    # Print pause positions and durations
    pause_info = []
    for i in range(0, len(pause_positions[0])):        
        pause_info.append({
                'pause_start': t[pause_positions[0][i]],
                'pause_finish': t[pause_positions[1][i]],
                'pause_duration': t[pause_positions[1][i]] - t[pause_positions[0][i]]
            })
    
    return pause_info, t