import math

def distance(point1, point2):
    return math.hypot(point2.x - point1.x, point2.y - point1.y)

def is_open_palm_flick(hand_landmarks):
    # All four fingers extended: tip above the pip joint
    fingers_extended = all([
        hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y,    # index finger
        hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y,  # middle finger
        hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y,  # ring finger
        hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y,  # pinky
    ])
    
    # Thumb extended — adjust for left/right hand by comparing x coords
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    thumb_open = abs(thumb_tip.x - thumb_ip.x) > 0.02  # a small threshold for "open" thumb
    
    return fingers_extended and thumb_open

def is_fist(hand_landmarks):
    wrist = hand_landmarks.landmark[0]
    tips = [hand_landmarks.landmark[i] for i in [8, 12, 16, 20]]
    # Fingers curled if tips close to wrist
    return all(distance(tip, wrist) < 0.1 for tip in tips)

def is_index_up(hand_landmarks):
    index_extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    other_fingers_folded = all([
        hand_landmarks.landmark[12].y > hand_landmarks.landmark[10].y,
        hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y,
        hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y,
    ])
    return index_extended and other_fingers_folded

# Removed is_two_hands_shield since no Protego spell anymore

