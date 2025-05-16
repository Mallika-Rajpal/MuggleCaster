import cv2
import numpy as np
import time
import os
from utils.hand_tracker import HandTracker
from utils.spell_detector import detect_spell
from utils.spell_effects import cast_spell
import pygame
import random

# --- Particle Classes ---

class Particle:
    def __init__(self, x, y, color=(255, 255, 200), radius_range=(3, 6), life=20):
        self.x = x
        self.y = y
        self.radius = random.randint(*radius_range)
        self.life = life
        self.color = color
        self.vx = 0
        self.vy = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.radius = max(0, self.radius - 0.1)

    def draw(self, frame):
        if self.life > 0 and self.radius > 0:
            alpha = int(255 * (self.life / 20))
            overlay = frame.copy()
            cv2.circle(overlay, (int(self.x), int(self.y)), int(self.radius), self.color, -1)
            cv2.addWeighted(overlay, alpha/255, frame, 1 - alpha/255, 0, frame)


class ExpelliarmusParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, color=(255, 255, 255), radius_range=(5, 8), life=15)
        # Fast horizontal velocity for swipe effect
        self.vx = random.uniform(20, 30)  # strong push right
        self.vy = random.uniform(-3, 3)   # slight vertical jitter


class AvadaKedavraParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, color=(0, 255, 0), radius_range=(8, 12), life=30)
        # Slow floating upwards
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-1.5, -0.5)


particles = []

def add_lumos_particles(frame, pos):
    for _ in range(5):
        p = Particle(pos[0] + random.randint(-10, 10),
                     pos[1] + random.randint(-10, 10),
                     color=(255, 255, 200),
                     radius_range=(3, 6),
                     life=20)
        p.vx = random.uniform(-0.5, 0.5)
        p.vy = random.uniform(-1.5, -0.5)
        particles.append(p)

def add_expelliarmus_particles(frame, pos):
    for _ in range(7):
        p = ExpelliarmusParticle(pos[0], pos[1] + random.randint(-5, 5))
        particles.append(p)

def add_avadakedavra_particles(frame, pos):
    for _ in range(5):
        p = AvadaKedavraParticle(pos[0] + random.randint(-15, 15),
                                 pos[1] + random.randint(-15, 15))
        particles.append(p)

def update_and_draw_particles(frame):
    for p in particles[:]:
        p.update()
        p.draw(frame)
        if p.life <= 0:
            particles.remove(p)


def play_sound(spell_name):
    try:
        sound_file = f"sounds/{spell_name.lower().replace(' ', '')}.mp3"
        if os.path.exists(sound_file):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        else:
            print(f"Sound file not found: {sound_file}")
    except Exception as e:
        print(f"Error playing sound for {spell_name}: {e}")


def main():
    pygame.mixer.init()
    cap = cv2.VideoCapture(0)
    detector = HandTracker()

    swipe_positions = []
    swipe_timestamps = []
    last_spell_time = 0
    spell_text = ""
    SPELL_COOLDOWN = 1.5

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = detector.find_hands(frame)
        hand_landmarks_list = detector.get_hand_landmarks_list()

        current_time = time.time()
        spell_cast = None

        if hand_landmarks_list:
            hand = hand_landmarks_list[0]
            h, w, _ = frame.shape
            idx_tip = hand.landmark[8]
            x, y = int(idx_tip.x * w), int(idx_tip.y * h)

            # Swipe tracking for Expelliarmus
            swipe_positions.append((x, y))
            swipe_timestamps.append(current_time)
            if len(swipe_positions) > 10:
                swipe_positions.pop(0)
                swipe_timestamps.pop(0)

            if len(swipe_positions) >= 2:
                x1, y1 = swipe_positions[0]
                x2, y2 = swipe_positions[-1]
                dt = swipe_timestamps[-1] - swipe_timestamps[0]
                dist = np.linalg.norm([x2 - x1, y2 - y1])
                speed = dist / dt if dt > 0 else 0

                if (speed > 800 and abs(y2 - y1) < 50 and (x2 - x1) > 100
                    and (current_time - last_spell_time) > SPELL_COOLDOWN):
                    spell_cast = "Expelliarmus"
                    swipe_positions.clear()
                    swipe_timestamps.clear()

            # Draw swipe trail
            for i in range(1, len(swipe_positions)):
                alpha = i / len(swipe_positions)
                color = (0, int(255 * alpha), int(255 * (1 - alpha)))
                cv2.line(frame, swipe_positions[i-1], swipe_positions[i], color, 8)

        else:
            swipe_positions.clear()
            swipe_timestamps.clear()

        # Detect other spells if no swipe spell
        if not spell_cast and hand_landmarks_list:
            spell = detect_spell(hand_landmarks_list)
            if spell and (current_time - last_spell_time) > SPELL_COOLDOWN:
                spell_cast = spell

        # Add spell particles depending on spell
        if spell_cast and hand_landmarks_list:
            hand = hand_landmarks_list[0]
            h, w, _ = frame.shape
            idx_tip = hand.landmark[8]
            x, y = int(idx_tip.x * w), int(idx_tip.y * h)

            if spell_cast == "Lumos":
                add_lumos_particles(frame, (x, y))
            elif spell_cast == "Expelliarmus":
                add_expelliarmus_particles(frame, (x, y))
            elif spell_cast == "Avada Kedavra":
                add_avadakedavra_particles(frame, (x, y))

        # Keep particles alive & drawing between casts (during cooldown)
        if spell_text and (current_time - last_spell_time) < SPELL_COOLDOWN and hand_landmarks_list:
            hand = hand_landmarks_list[0]
            h, w, _ = frame.shape
            idx_tip = hand.landmark[8]
            x, y = int(idx_tip.x * w), int(idx_tip.y * h)

            if spell_text[:-1] == "Lumos":
                add_lumos_particles(frame, (x, y))
            elif spell_text[:-1] == "Expelliarmus":
                add_expelliarmus_particles(frame, (x, y))
            elif spell_text[:-1] == "Avada Kedavra":
                add_avadakedavra_particles(frame, (x, y))

        update_and_draw_particles(frame)

        # Show spell effects & play sound
        if spell_cast:
            spell_text = spell_cast + "!"
            last_spell_time = current_time
            play_sound(spell_cast)

        if spell_text and (current_time - last_spell_time) < SPELL_COOLDOWN:
            frame = cast_spell(spell_text[:-1], frame)
            cv2.putText(frame, spell_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                        2, (255, 255, 255), 5, cv2.LINE_AA)
        else:
            spell_text = ""

        cv2.imshow("The MuggleCaster - Magic, the Muggle Way", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()





