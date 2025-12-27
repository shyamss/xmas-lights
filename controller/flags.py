import math

def anim_gemini(current_state, state, step, num_leds):
    # 1. Extensive Flag Database
    if 'flags' not in state:
        state['flags'] = [
            ("USA", [(178, 34, 52), (255, 255, 255), (60, 59, 110)]),
            ("Canada", [(255, 0, 0), (255, 255, 255), (255, 0, 0)]),
            ("Mexico", [(0, 104, 71), (255, 255, 255), (206, 17, 38)]),
            ("Brazil", [(0, 156, 59), (255, 223, 0), (0, 39, 118)]),
            ("UK", [(1, 33, 105), (255, 255, 255), (200, 16, 46)]),
            ("France", [(0, 35, 149), (255, 255, 255), (237, 41, 57)]),
            ("Germany", [(0, 0, 0), (221, 0, 0), (255, 206, 0)]),
            ("Italy", [(0, 146, 70), (255, 255, 255), (206, 43, 52)]),
            ("Spain", [(170, 21, 27), (241, 191, 0), (170, 21, 27)]),
            ("Portugal", [(0, 102, 0), (255, 0, 0)]),
            ("Ireland", [(22, 155, 98), (255, 255, 255), (255, 136, 62)]),
            ("Netherlands", [(174, 28, 40), (255, 255, 255), (33, 70, 139)]),
            ("Belgium", [(0, 0, 0), (255, 233, 54), (255, 15, 33)]),
            ("Switzerland", [(255, 0, 0), (255, 255, 255)]),
            ("Sweden", [(0, 107, 168), (254, 204, 2)]),
            ("Norway", [(186, 12, 47), (255, 255, 255), (0, 32, 91)]),
            ("Denmark", [(191, 12, 45), (255, 255, 255)]),
            ("Finland", [(255, 255, 255), (0, 53, 128)]),
            ("Greece", [(13, 94, 175), (255, 255, 255)]),
            ("Ukraine", [(0, 87, 183), (255, 215, 0)]),
            ("Turkey", [(227, 10, 23), (255, 255, 255)]),
            ("India", [(255, 153, 51), (255, 255, 255), (18, 128, 1)]),
            ("Pakistan", [(1, 65, 28), (255, 255, 255)]),
            ("Japan", [(255, 255, 255), (188, 0, 45), (255, 255, 255)]),
            ("South Korea", [(255, 255, 255), (205, 46, 58), (5, 78, 162), (0, 0, 0)]),
            ("China", [(238, 28, 37), (255, 222, 0)]),
            ("Thailand", [(165, 25, 49), (255, 255, 255), (45, 42, 74)]),
            ("Vietnam", [(218, 37, 29), (255, 255, 0)]),
            ("Indonesia", [(255, 0, 0), (255, 255, 255)]),
            ("Australia", [(1, 33, 105), (255, 255, 255), (228, 0, 43)]),
            ("New Zealand", [(1, 33, 105), (255, 255, 255), (200, 16, 46)]),
            ("South Africa", [(224, 60, 49), (0, 124, 89), (0, 35, 149), (255, 255, 255), (0, 0, 0), (255, 184, 28)]),
            ("Egypt", [(206, 17, 38), (255, 255, 255), (0, 0, 0)]),
            ("Nigeria", [(0, 135, 81), (255, 255, 255), (0, 135, 81)]),
            ("Kenya", [(0, 0, 0), (187, 0, 0), (0, 102, 0)]),
            ("Morocco", [(193, 39, 45), (0, 98, 51)]),
            ("Argentina", [(117, 170, 219), (255, 255, 255), (117, 170, 219)]),
            ("Colombia", [(255, 205, 0), (0, 48, 135), (206, 17, 38)]),
            ("Chile", [(255, 255, 255), (0, 57, 166), (213, 43, 30)]),
            ("Jamaica", [(0, 155, 58), (255, 242, 0), (0, 0, 0)]),
            ("Israel", [(255, 255, 255), (0, 56, 184), (255, 255, 255)]),
            ("Saudi Arabia", [(0, 108, 53), (255, 255, 255)])
        ]
        state['flag_index'] = 0
        state['fps'] = 30 
        state['hold_frames'] = 10 * state['fps'] # 10 seconds per flag
        state['timer'] = 0

    # 2. Timing Logic
    state['timer'] += 1
    if state['timer'] >= state['hold_frames']:
        state['timer'] = 0
        state['flag_index'] = (state['flag_index'] + 1) % len(state['flags'])

    # 3. Rendering
    name, colors = state['flags'][state['flag_index']]
    num_colors = len(colors)
    pixels_per_color = num_leds // num_colors
    
    new_led_state = []
    for i in range(num_leds):
        color_idx = i // pixels_per_color
        if color_idx >= num_colors:
            color_idx = num_colors - 1
            
        base_color = colors[color_idx]
        
        # Waving fabric shimmer effect
        wave = 0.85 + 0.15 * math.sin(step * 0.15 + i * 0.3)
        
        new_led_state.append((
            int(base_color[0] * wave),
            int(base_color[1] * wave),
            int(base_color[2] * wave)
        ))

    return new_led_state
