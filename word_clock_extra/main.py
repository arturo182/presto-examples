import time
import random

import machine
import ntptime
import plasma
from picovector import ANTIALIAS_NONE, PicoVector, Transform
from presto import Presto

# Setup for the Presto display
presto = Presto()
display = presto.display
vector = PicoVector(display)
WIDTH, HEIGHT = display.get_bounds()

# Timezone offset, can be + or -
UTC_OFFSET = 1

# Show the time in all white
BORING_MODE = False


rtc = machine.RTC()
words = [
    "presto", "p", "it", "i", "is", "m",
    "o", "quarter", "ronir",
    "ea", "twenty", "l", "five",
    "half", "lyco", "ten", "ok",
    "ed", "minutes", "xthi",
    "s", "to", "isxase", "past",
    "c", "four", "re", "seven", "t",
    "twelve", "xmsgfro",
    "m", "nine", "ar", "five", "tu",
    "two", "r", "eight", "ohav",
    "e", "eleven", "ani", "six",
    "ce", "three", "da", "one", "y",
    "all", "ten", "o'clock"
    ]


# WiFi setup
print('Connecting...')
wifi = presto.connect()


# Set the correct time using the NTP service.
print('Getting time...')
ntptime.settime()


vector.set_antialiasing(ANTIALIAS_NONE)
vector.set_font("QuinqueFive.af", 11)

t = Transform()
vector.set_transform(t) 


BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(200, 200, 200)
LIGHT_GRAY = display.create_pen(40, 40, 40)
GRAY = display.create_pen(30, 30, 30)
COLORS = [
    display.create_pen(220, 30, 30), # red
    display.create_pen(250, 165, 30), # orange
    display.create_pen(220, 215, 55), # yellow
    display.create_pen(0, 128, 40), # green
    display.create_pen(40, 64, 140), # blue
    display.create_pen(100, 40, 110), # purple
    display.create_pen(250, 100, 180), # pink
    display.create_pen(100, 200, 250) # light blue
]


# Assign the colors to the backlight
leds = plasma.WS2812(7, 0, 0, 33)
leds.start()
for i in range(8):
    leds.set_hsv(i, 0.0 if BORING_MODE else i / 7.0, not BORING_MODE, 0.5);
 

def approx_time(hours, minutes):
    nums = {0: "twelve", 1: "one", 2: "two",
            3: "three", 4: "four", 5: "five", 6: "six",
            7: "seven", 8: "eight", 9: "nine", 10: "ten",
            11: "eleven", 12: "twelve"}

    text = "it is "

    if hours == 12:
        hours = 0

    if minutes >= 5 and minutes < 10:
        text += "five minutes past " + nums[hours]
    elif minutes >= 10 and minutes < 15:
        text += "ten minutes past " + nums[hours]
    elif minutes >= 15 and minutes < 20:
        text += "quarter past " + nums[hours]
    elif minutes >= 20 and minutes < 25:
        text += "twenty minutes past " + nums[hours]
    elif minutes >= 25 and minutes < 30:
        text += "twenty five minutes past " + nums[hours]
    elif minutes >= 30 and minutes < 35:
        text += "half past " + nums[hours]
    elif minutes >= 35 and minutes < 40:
        text += "twenty five minutes to " + nums[hours + 1]
    elif minutes >= 40 and minutes < 45:
        text += "twenty minutes to " + nums[hours + 1]
    elif minutes >= 45 and minutes < 50:
        text += "quarter to " + nums[hours + 1]
    elif minutes >= 50 and minutes < 55:
        text += "ten minutes to " + nums[hours + 1]
    elif minutes >= 55 and minutes <= 59:
        text += "five minutes to " + nums[hours + 1]
    else:
        text += nums[hours] + " o'clock"
    
    return text


def update():
    # grab the current time from the ntp server and update the Pico RTC
    try:
        ntptime.settime()
    except OSError:
        print("Unable to contact NTP server")

    current_t = time.gmtime(time.time() + UTC_OFFSET * 60 * 60)
    time_string = approx_time(current_t[3] - 12 if current_t[3] > 12 else current_t[3], current_t[4])
    time_words = time_string.split()

    print(f'{current_t[3]:02d}:{current_t[4]:02d} - {time_words}')
    
    return time_words


def draw(time_words):
    # Clear the screen
    display.set_pen(BLACK)
    display.clear()

    default_x = 12
    x = default_x
    y = 22

    line_space = 17
    letter_space = 17
    margin = 10
    scale = 1
    spacing = 1
    
    colors = COLORS.copy()
    
    for word in words:        
        if len(time_words) and word == time_words[0]:
            if len(colors) and not BORING_MODE:
                display.set_pen(colors.pop(0))
            else:
                display.set_pen(WHITE)
                
            time_words.pop(0)
        elif word == "presto":
            display.set_pen(LIGHT_GRAY)
        else:
            display.set_pen(GRAY)

        for letter in word:
            mx, my, mw, mh = vector.measure_text(letter.upper())
            if not x + mw <= WIDTH - margin:
                y += line_space
                x = default_x

            vector.text(letter.upper(), x, y)
            x += letter_space

    presto.update()
    

while True:
    time_words = update()
    
    draw(time_words)
    
    # Update every minute
    time.sleep(60)

