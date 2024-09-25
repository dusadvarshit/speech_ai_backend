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


def pace_feedback(pace_score, articulation_rate):
    
    text = ''
    text_list = []
    if pace_score>=85:
        temp_lst = ['Great job!', 'Great work!', 'Excellent!', 'Bravo!', 'Amazing work!', 'Exemplary work!', 
                   ]
        
        random.shuffle(temp_lst)
        text += """{} Your pace is in recommended limit and will be easy to follow for most of your audience.""".format(temp_lst[0])
        text_list += [temp_lst[0], """Your pace is in recommended limit and will be easy to follow for most of your audience."""]
    
    elif pace_score>=60:
        temp_lst = ['Good job!', 'Good work!', 'Well done!', 'Nice!']
        random.shuffle(temp_lst)
        text += """{} Your pace needs more work to make it more interesting for the audience. Slow speaking overall bores the audience and their attention wanders away.""".format(temp_lst[0])
        text_list += [temp_lst[0], """Your pace needs more work to make it more interesting for the audience. Slow speaking overall bores the audience and their attention wanders away."""]
        
    elif pace_score<60:
        temp_lst = ['Satisfactory!', 'OK!', 'Not great!', 'You can do better!']
        random.shuffle(temp_lst)
        
        if articulation_rate>240:
            text += """{} Your pace is too fast for the audience to follow. Try practicing tongue twisters to slow yourself down which will make your enunciation better and clearer.""".format(temp_lst[0])
            text_list += [temp_lst[0], """Your pace is too fast for the audience to follow. Try practicing tongue twisters to slow yourself down which will make your enunciation better and clearer."""]
        else:
            text += """{} Your pace is too slow and dull which will lose audience attention. Speed up the pace by trying speed reading with speaking which will develop the muscular strength and skill to speak faster.""".format(temp_lst[0])
            text_list += [temp_lst[0], """Your pace is too slow and dull which will lose audience attention. Speed up the pace by trying speed reading with speaking which will develop the muscular strength and skill to speak faster."""]
        
    return text, text_list



def speech_rate(filename):
    cols = ['soundname', 'nsyll', 'npause', 'dur(s)', 'phonationtime(s)', 'speechrate(nsyll / dur)', 'articulation '
        'rate(nsyll / phonationtime)', 'ASD(speakingtime / nsyll)']
    
    silencedb = -25
    mindip = 2
    minpause = 0.3
    sound = parselmouth.Sound(filename)
    originaldur = sound.get_total_duration()
    intensity = sound.to_intensity(50)
    start = call(intensity, "Get time from frame number", 1)
    nframes = call(intensity, "Get number of frames")
    end = call(intensity, "Get time from frame number", nframes)
    min_intensity = call(intensity, "Get minimum", 0, 0, "Parabolic")
    max_intensity = call(intensity, "Get maximum", 0, 0, "Parabolic")

    # get .99 quantile to get maximum (without influence of non-speech sound bursts)
    max_99_intensity = call(intensity, "Get quantile", 0, 0, 0.99)

    # estimate Intensity threshold
    threshold = max_99_intensity + silencedb
    threshold2 = max_intensity - max_99_intensity
    threshold3 = silencedb - threshold2
    if threshold < min_intensity:
        threshold = min_intensity

    # get pauses (silences) and speakingtime
    textgrid = call(intensity, "To TextGrid (silences)", threshold3, minpause, 0.1, "silent", "sounding")
    silencetier = call(textgrid, "Extract tier", 1)
    silencetable = call(silencetier, "Down to TableOfReal", "sounding")
    npauses = call(silencetable, "Get number of rows")
    speakingtot = 0
    for ipause in range(npauses):
        pause = ipause + 1
        beginsound = call(silencetable, "Get value", pause, 1)
        endsound = call(silencetable, "Get value", pause, 2)
        speakingdur = endsound - beginsound
        speakingtot += speakingdur

    intensity_matrix = call(intensity, "Down to Matrix")
    # sndintid = sound_from_intensity_matrix
    sound_from_intensity_matrix = call(intensity_matrix, "To Sound (slice)", 1)
    # use total duration, not end time, to find out duration of intdur (intensity_duration)
    # in order to allow nonzero starting times.
    intensity_duration = call(sound_from_intensity_matrix, "Get total duration")
    intensity_max = call(sound_from_intensity_matrix, "Get maximum", 0, 0, "Parabolic")
    point_process = call(sound_from_intensity_matrix, "To PointProcess (extrema)", "Left", "yes", "no", "Sinc70")
    # estimate peak positions (all peaks)
    numpeaks = call(point_process, "Get number of points")
    t = [call(point_process, "Get time from index", i + 1) for i in range(numpeaks)]

    # fill array with intensity values
    timepeaks = []
    peakcount = 0
    intensities = []
    for i in range(numpeaks):
        value = call(sound_from_intensity_matrix, "Get value at time", t[i], "Cubic")
        if value > threshold:
            peakcount += 1
            intensities.append(value)
            timepeaks.append(t[i])

    # fill array with valid peaks: only intensity values if preceding
    # dip in intensity is greater than mindip
    validpeakcount = 0
    currenttime = timepeaks[0]
    currentint = intensities[0]
    validtime = []

    for p in range(peakcount - 1):
        following = p + 1
        followingtime = timepeaks[p + 1]
        dip = call(intensity, "Get minimum", currenttime, timepeaks[p + 1], "None")
        diffint = abs(currentint - dip)
        if diffint > mindip:
            validpeakcount += 1
            validtime.append(timepeaks[p])
        currenttime = timepeaks[following]
        currentint = call(intensity, "Get value at time", timepeaks[following], "Cubic")

    # Look for only voiced parts
    pitch = sound.to_pitch_ac(0.02, 30, 4, False, 0.03, 0.25, 0.01, 0.35, 0.25, 450)
    voicedcount = 0
    voicedpeak = []

    for time in range(validpeakcount):
        querytime = validtime[time]
        whichinterval = call(textgrid, "Get interval at time", 1, querytime)
        whichlabel = call(textgrid, "Get label of interval", 1, whichinterval)
        value = pitch.get_value_at_time(querytime) 
        if not math.isnan(value):
            if whichlabel == "sounding":
                voicedcount += 1
                voicedpeak.append(validtime[time])

    # calculate time correction due to shift in time for Sound object versus
    # intensity object
    timecorrection = originaldur / intensity_duration

    # Insert voiced peaks in TextGrid
    call(textgrid, "Insert point tier", 1, "syllables")
    for i in range(len(voicedpeak)):
        position = (voicedpeak[i] * timecorrection)
        call(textgrid, "Insert point", 1, position, "")

    # return results
    speakingrate = voicedcount / originaldur
    articulationrate = voicedcount / speakingtot
    npause = npauses - 1
    asd = speakingtot / voicedcount
    speechrate_dictionary = {'soundname':filename,
                             'nsyll':voicedcount,
                             'npause': npause,
                             'dur(s)':originaldur,
                             'phonationtime(s)':intensity_duration,
                             'speechrate(nsyll / dur)': speakingrate,
                             "articulation rate(nsyll / phonationtime)":articulationrate,
                             "ASD(speakingtime / nsyll)":asd}
    return speechrate_dictionary


def compute_articulation_rate(file_location):
    try:
        speechrate_dictionary = speech_rate(file_location)
        articulation_rate = speechrate_dictionary['articulation rate(nsyll / phonationtime)']
    except:
        articulation_rate = 0

    articulation_rate = articulation_rate*60
    pace_score = np.round((1 - (abs(240-articulation_rate))/240)*100)
        
    return articulation_rate, pace_score