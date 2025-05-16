import cv2

def cast_spell(spell_name, frame):
    height, width, _ = frame.shape

    if spell_name == "Expelliarmus":
        cv2.putText(frame, "Expelliarmus!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, (0, 0, 255), 3)
        cv2.circle(frame, (width // 2, height // 2), 80, (0, 0, 255), 5)

    elif spell_name == "Avada Kedavra":
        cv2.putText(frame, "Avada Kedavra!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, (0, 255, 0), 3)
        cv2.circle(frame, (width // 2, height // 2), 120, (0, 255, 0), -1)
        cv2.line(frame, (width // 2, 0), (width // 2, height), (0, 255, 0), 8)  # Death beam

    elif spell_name == "Lumos":
        cv2.putText(frame, "Lumos!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, (255, 255, 0), 3)
        cv2.circle(frame, (width // 2, height // 2), 150, (255, 255, 200), -1)

    return frame

