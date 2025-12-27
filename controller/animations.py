import math
import random
import gemini

def anim_rainbow_sine(current_state, state, step, num_leds):
    new_state = []
    for i in range(num_leds):
        r = int(127 * (1 + math.sin(0.1 * i + 0.1 * step)))
        g = int(127 * (1 + math.sin(0.1 * i + 0.1 * step + 2)))
        b = int(127 * (1 + math.sin(0.1 * i + 0.1 * step + 4)))
        new_state.append((r, g, b))
    return new_state

def anim_comet_tail(current_state, state, step, num_leds):
    # Fade previous state
    new_state = [(int(r*0.9), int(g*0.9), int(b*0.9)) for r, g, b in current_state]
 
    num_comets = 4 
    pos = step % num_leds
    for i in range(num_comets):
        #new_state[pos] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        #new_state[pos] = (random.randint(0,255), random.randint(0,100), 0)
        if not 'comet_colors' in state:
            state['comet_colors'] = {}
        state['comet_colors'][i] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        new_state[pos] = (0,random.randint(0,255), random.randint(0,100))
        pos = (pos + int(num_leds / num_comets)) % num_leds

    return new_state

def anim_sledding(current_state, state, step, num_leds):
    print(state)
    if not 'sled_pos' in state:
        state['sled_pos'] = 0.0
        state['velocity'] = 0.001
    else:
        sled_pos = state['sled_pos']
        velocity = state['velocity']

        sled_pos = sled_pos + velocity
        velocity = min(velocity * 1.1, 2)

        if int(sled_pos) > num_leds:
            sled_pos = 0
            velocity = 0.01

        state['sled_pos'] = sled_pos
        state['velocity'] = velocity

    new_led_state = [(int(r*0.4), int(g*0.4), int(b*0.4)) for r, g, b in current_state]
    
    pos = num_leds - int(state['sled_pos']) - 1
    print(pos)
    new_led_state[pos] = (255, 255, 255)

    return new_led_state


def anim_random(current_state, state, step, num_leds):
    new_led_state = [(int(r*0.7), int(g*0.7), int(b*0.9)) for r, g, b in current_state]
    if step % 10 > 0:
        return new_led_state
    num_lights = min(random.randint(0, num_leds - 1), 10)
    for i in range(num_lights):
        pos = random.randint(0, num_leds - 1)
        #new_led_state[pos] = (random.randint(0,255), random.randint(0,255), random.randint(0,255)) 
        new_led_state[pos] = (random.randint(0,10), random.randint(0,10), random.randint(0,255)) 
    return new_led_state

def anim_fire_flicker(current_state, state, step, num_leds):
    return [(255, 70 + random.randint(0, 80), 0) for _ in range(num_leds)]

def anim_off(current_state, state, step, num_leds):
    return [(0, 0, 0)] * num_leds

def anim_comet_spectrum(current_state, state, step, num_leds):
    """A comet that cycles through the color spectrum as it moves."""

    # 1. Fade the previous state (the trail)
    # We multiply by 0.85 to leave a nice lingering trail
    new_state = [(int(r*0.92), int(g*0.92), int(b*0.92)) for r, g, b in current_state]

    # 2. Determine the comet's position
    pos = step % num_leds

    # 3. Determine the comet's current color based on the step
    # This cycles the color once every 256 steps
    color_pos = step % 256

    # The 'Wheel' math to get a spectrum color
    if color_pos < 85:
        head_color = (color_pos * 3, 255 - color_pos * 3, 0)
    elif color_pos < 170:
        color_pos -= 85
        head_color = (255 - color_pos * 3, 0, color_pos * 3)
    else:
        color_pos -= 170
        head_color = (0, color_pos * 3, 255 - color_pos * 3)

    # 4. Set the 'Head' of the comet
    new_state[pos] = head_color

    return new_state

def anim_steady_white(current_state, state, step, num_leds):
    """Sets every LED to pure white."""
    return [(200, 150, 80)] * num_leds


# The Map is stored here so the main script can import it
ANIMATION_MAP = {
    "rainbow": anim_rainbow_sine,
    "comet": anim_comet_tail,
    "comet2": anim_comet_spectrum,  # Add this line
    "fire": anim_fire_flicker,
    "white": anim_steady_white,
    "sledding": anim_sledding,
    "random": anim_random,
    "gemini": gemini.anim_gemini,
    "off": anim_off
}
