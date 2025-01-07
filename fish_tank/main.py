import time
import random
import pngdec
import ntptime

import machine
from presto import Presto
from picovector import ANTIALIAS_NONE, PicoVector, Transform

# Should the time be shown?
SHOW_TIME = True

# Timezone offset, can be + or -
UTC_OFFSET = 1


presto = Presto(full_res=False, ambient_light=True)
display = presto.display
vector = PicoVector(display)
WIDTH, HEIGHT = display.get_bounds()

YELLOW = display.create_pen(255, 205, 0)
WHITE = display.create_pen(255, 255, 255)

SPRITE_SIZE = 30

if SHOW_TIME:
    rtc = machine.RTC()

    # WiFi setup
    print('Connecting...')
    wifi = presto.connect()

    # Set the correct time using the NTP service.
    print('Getting time...')
    ntptime.settime()

    vector.set_antialiasing(ANTIALIAS_NONE)
    vector.set_font("cherry-hq.af", 60)

    t = Transform()
    vector.set_transform(t)

display.set_layer(0)

bg = pngdec.PNG(display)
bg.open_file("fish_bg.png")
bg.decode(0, 0)
    
presto.update()

display.set_layer(1)

class Fish:
    def __init__(self, x, y, file_left, file_right):
        self.x = x
        self.y = y
        
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        
        self.speed = 1.0
        
        self.png_left = pngdec.PNG(display)
        self.png_left.open_file(file_left)
        
        self.png_right = pngdec.PNG(display)
        self.png_right.open_file(file_right)

        self.facing_left = self.dx < 0
        self.flip_thresh = 0.2

    def move(self, width, height):
        self.dx += random.uniform(-0.1, 0.1)
        self.dy += random.uniform(-0.1, 0.1)

        mag = (self.dx ** 2 + self.dy ** 2) ** 0.5
        if mag > 0:
            self.dx = (self.dx / mag) * self.speed
            self.dy = (self.dy / mag) * self.speed

        self.x += self.dx
        self.y += self.dy

        if self.x < 0 or self.x + SPRITE_SIZE > width:
            self.dx *= -1
        if self.y < 0 or self.y + SPRITE_SIZE > height:
            self.dy *= -1

        if self.dx < -self.flip_thresh and not self.facing_left:
            self.facing_left = True
        elif self.dx > self.flip_thresh and self.facing_left:
            self.facing_left = False
    
    def draw(self):
        if self.facing_left:
            self.png_left.decode(int(f.x), int(f.y))
        else:
            self.png_right.decode(int(f.x), int(f.y))

images = [
    ['fish_red_left.png', 'fish_red_right.png'],
    ['fish_blue_left.png', 'fish_blue_right.png'],
    ['fish_purple_left.png', 'fish_purple_right.png']
]

fish = []

for imgs in images:
    f = Fish(random.uniform(SPRITE_SIZE, WIDTH - SPRITE_SIZE), random.uniform(SPRITE_SIZE, HEIGHT - SPRITE_SIZE), imgs[0], imgs[1])
    f.speed = random.uniform(0.3, 0.6)
    fish.append(f)

if SHOW_TIME:
    def update_time_str():
        try:
            ntptime.settime()
        except OSError:
            print("Unable to contact NTP server")

        current_t = time.gmtime(time.time() + UTC_OFFSET * 60 * 60)
        time_str = f'{current_t[3]:02d}:{current_t[4]:02d}'
        
        return time_str

    time_str = update_time_str()
    prev_update = time.time()
prev_fps_update = time.time()
fps = 0

while True:
    if SHOW_TIME:
        if time.time() - prev_update >= 60:
            time_str = update_time_str()
            prev_update = time.time()
    
    display.set_pen(0)
    display.clear()
    
    if SHOW_TIME:
        _, _, w, _ = vector.measure_text(time_str)
        cx = int(WIDTH // 2 - w // 2)

        display.set_pen(WHITE)
        vector.text(time_str, cx + 2, 96)
        
        display.set_pen(YELLOW)
        vector.text(time_str, cx, 94)
    
    for f in fish:
        f.move(WIDTH, HEIGHT)
        f.draw()
    
    presto.update()
    
    fps += 1
    if time.time() - prev_fps_update >= 1.0:
        print(f'FPS: {fps}')
        prev_fps_update = time.time()
        fps = 0