from utils.hand_gestures import (
    is_open_palm_flick,
    is_fist,
    is_index_up
)

def detect_spell(hand_landmarks_list):
    if len(hand_landmarks_list) == 0:
        return None

    hand = hand_landmarks_list[0]

    if is_open_palm_flick(hand):
        return "Expelliarmus"
    elif is_fist(hand):
        return "Avada Kedavra"
    elif is_index_up(hand):
        return "Lumos"
    else:
        return None

