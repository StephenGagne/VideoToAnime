'profile_detection.py' is used to detect and crop faces detected at a side-view (left and right) angle

'frontal_detection.py' is used to detect and crop faces displayed at a frontal view.

There is some overlap, whereby the each model detects faces from the other perspective.

=======================================================================================

NOTES:
    The profile detection model is not perfect, and will generate 'dud' images that for now, need
    to be deleted manually. See instructions below. 

STEPS:

PART 1: GENERATE PROFILE FACES
    1. Run profile_detection.py - this will generate the left-facing images -> './side_faces'
    2. Manually cd into generated folder 'side_faces'
    3. Prune/delete unecessary photos (duds and frontal views)
    4. Run flip_faces.py - this will generate the right-facing images

PART 2: GENERATE FRONTAL FACES
    1. Run frontal_detection.py
    2. Prune/delete any unecessary 'dud' photos

