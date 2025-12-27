import math
import random

def anim_gemini(current_state, state, step, num_leds):
    if 'seeds' not in state:
        # Create multiple overlapping wave centers with different speeds/directions
        state['seeds'] = [
            {'speed': 0.03, 'freq': 0.08, 'phase': 0.0},
            {'speed': -0.05, 'freq': 0.04, 'phase': 2.0},
            {'speed': 0.02, 'freq': 0.12, 'phase': 4.5}
        ]

    new_led_state = []

    for i in range(num_leds):
        # Calculate interference pattern from multiple oscillators
        noise = 0
        for s in state['seeds']:
            noise += math.sin(step * s['speed'] + i * s['freq'] + s['phase'])
        
        # Normalize to 0.0 - 1.0 range and sharpen contrast
        # Squaring the result creates wider "black" valleys and tighter "white" peaks
        intensity = ((noise / len(state['seeds'])) + 1) / 2
        intensity = intensity ** 2.5
        
        # Smoothly oscillate between Gold and Silver based on position and time
        color_mix = (math.sin(step * 0.01 + i * 0.05) + 1) / 2
        
        # Gold: (255, 180, 20) | Silver: (200, 200, 220)
        r_gold, g_gold, b_gold = 255, 180, 20
        r_silv, g_silv, b_silv = 200, 200, 220
        
        # Blend colors
        target_r = (r_gold * color_mix) + (r_silv * (1 - color_mix))
        target_g = (g_gold * color_mix) + (g_silv * (1 - color_mix))
        target_b = (b_gold * color_mix) + (b_silv * (1 - color_mix))
        
        # Apply the undulating intensity (0.0 to 1.0)
        new_led_state.append((
            int(target_r * intensity),
            int(target_g * intensity),
            int(target_b * intensity)
        ))

    return new_led_state
