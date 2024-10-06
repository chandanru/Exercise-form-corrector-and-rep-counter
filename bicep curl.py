#Bicep Curls
#FINAL UI CHANGED CODE 
import cv2
import mediapipe as mp
import numpy as np

# Initialize variables
counter = 0
stage = None
target_reps = 12  # Total reps for one set
sets_completed = 0
display_set_completed = False
waiting_for_next_set = False

# Initialize MediaPipe pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Video capture
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Camera not accessible.")
    exit()

def calculate_angle(a, b, c):
    a = np.array(a)  # First point
    b = np.array(b)  # Mid point
    c = np.array(c)  # End point

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Helper function to draw rounded rectangles
def draw_rounded_box(image, top_left, bottom_right, color, thickness):
    pts_outer = np.array([top_left, [bottom_right[0], top_left[1]], bottom_right, [top_left[0], bottom_right[1]]], np.int32)
    cv2.polylines(image, [pts_outer], isClosed=True, color=color, thickness=thickness, lineType=cv2.LINE_AA)

# Helper function to draw text with border
def draw_text_with_border(image, text, position, font, scale, color, thickness, border_color, border_thickness):
    cv2.putText(image, text, position, font, scale, border_color, border_thickness, cv2.LINE_AA)
    cv2.putText(image, text, position, font, scale, color, thickness, cv2.LINE_AA)

# MediaPipe Pose model setup
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture image.")
            break

        # Convert the image to RGB and process with MediaPipe
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract pose landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates for shoulder, elbow, wrist
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)

            # Visualize the angle with a border
            draw_text_with_border(image, str(int(angle)),
                                  tuple(np.multiply(elbow, [frame.shape[1], frame.shape[0]]).astype(int)),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, (0, 0, 0), 3)

            # Logic for counting reps, only if not waiting for the next set
            if not waiting_for_next_set:
                if angle > 160:
                    stage = "down"
                if angle < 30 and stage == 'down':
                    stage = "up"
                    counter += 1
                    print(counter)

        except Exception as e:
            print(f"Error: {e}")

        # Draw left-hand side box for REPS and STAGE
        draw_rounded_box(image, (0, 0), (225, 73), (50, 50, 50), 5)  # Outer box
        draw_rounded_box(image, (10, 10), (215, 63), (255, 255, 255), 2)  # Inner box

        # Display REPS and counter with border
        draw_text_with_border(image, 'REPS', (30, 25), cv2.FONT_HERSHEY_DUPLEX, 0.4, (255, 255, 255), 1, (0, 0, 0), 2)
        draw_text_with_border(image, str(counter), (30, 55), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, (0, 0, 0), 2)

        # Display STAGE with border
        draw_text_with_border(image, 'STAGE', (100, 25), cv2.FONT_HERSHEY_DUPLEX, 0.4, (255, 255, 255), 1, (0, 0, 0), 2)
        draw_text_with_border(image, stage, (100, 55), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, (0, 0, 0), 2)

        # Draw the right-hand side progress bar
        bar_top_left = (550, 50)
        bar_bottom_right = (590, 450)
        bar_height = 400  # Total height of the progress bar
        fill_height = int(bar_height * (counter / target_reps))  # Calculate fill height based on reps

        # Outer box of the progress bar
        draw_rounded_box(image, bar_top_left, bar_bottom_right, (50, 50, 50), 5)

        # Draw progress bar fill
        cv2.rectangle(image, (bar_top_left[0], bar_bottom_right[1] - fill_height),
                      bar_bottom_right, (255, 255, 255), -1)

        # Show progress as a percentage with border
        progress_percentage = int((counter / target_reps) * 100)
        draw_text_with_border(image, f'Set progress {progress_percentage}%', (bar_top_left[0] - 60, bar_top_left[1] - 20),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, (0, 0, 0), 3)

        # Check if one set is completed (reps == 12)
        if counter >= target_reps and not waiting_for_next_set:
            display_set_completed = True
            sets_completed += 1
            waiting_for_next_set = True  # Set flag to wait for key press
            counter = 0  # Reset the counter for the next set

        # Display "Set Completed" message
        if display_set_completed:
            
            draw_text_with_border(image, '1 Set Completed! Press SPACE to start next set', (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                  (58, 95, 11), 1, (0, 0, 0), 3)

        # Display the number of sets completed at the bottom left corner
        draw_rounded_box(image, (20, frame.shape[0] - 80), (250, frame.shape[0] - 20), (128, 128, 128), 2)
        draw_rounded_box(image, (30, frame.shape[0] - 70), (240, frame.shape[0] - 30), (255, 255, 255), 2)
        draw_text_with_border(image, f'Sets Completed: {sets_completed}', (45, frame.shape[0] - 43),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, (0, 0, 0), 3)

        # Show the image with the overlay
        cv2.imshow('Pose Estimation', image)

        # Wait for key press to start the next set
        key = cv2.waitKey(10)
        if waiting_for_next_set and key == ord(' '):
            waiting_for_next_set = False  # Reset the flag to allow new reps
            display_set_completed = False  # Remove the "Set Completed" message

        # Break the loop if 'q' is pressed
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()