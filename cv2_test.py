import numpy as np
import cv2 as cv
from color import name_to_bgr, detect_bgr, rect_average

REGION_SIZE = 20
 
cap = cv.VideoCapture(1, cv.CAP_DSHOW)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

cap.set(cv.CAP_PROP_AUTO_WB, 0.0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
 
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here
   
    r, frame = cap.read()

    # gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Display the resulting frame
    cv.imshow('frame', frame)

# Drawing region 0 at: [30, 160]
# Drawing region 1 at: [120, 160]
# Drawing region 2 at: [210, 160]
# Drawing region 3 at: [30, 250]
# Drawing region 4 at: [120, 250]
# Drawing region 5 at: [210, 250]
# Drawing region 6 at: [30, 340]
# Drawing region 7 at: [120, 340]
# Drawing region 8 at: [210, 340]

    x = 120
    y = 330

    rect  = frame[y:y+REGION_SIZE, x:x+REGION_SIZE]
    cv.rectangle(frame, (x,y), (x+REGION_SIZE, y+REGION_SIZE), (255, 255, 255), 2)

    average_col = rect_average(rect)
    print(f"Average color in rectangle at ({x}, {y}): {average_col}")


    color = detect_bgr(rect_average(rect))[0]
    print(f"Color at ({x}, {y}): {color}")


    if cv.waitKey(1) == ord('q'):
        break
 
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()