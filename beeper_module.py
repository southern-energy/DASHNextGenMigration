#Beeper Module

# Adding a Beep for when the program finishes.
import winsound
import time

def beep_when_done():
    #Attributes
    duration_short = 100  # milliseconds
    duration_long = 300  # milliseconds
    freq = 400  # Hz

    winsound.Beep(freq, duration_short)
    winsound.Beep(freq, duration_long)
    winsound.Beep(freq, duration_short)

beep_when_done()