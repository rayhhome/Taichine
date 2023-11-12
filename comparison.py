import json
import numpy as np
import math
import sys
import subprocess
import argparse
import os
# sys.path.append("..")
from OpenPoseInter import parseImageFromPath
import pygame

# Prereq: Opened folder in Openpose Root Dir
def play_wav_file(file_path):
    pygame.init()
    pygame.mixer.init()

    try:
        sound = pygame.mixer.Sound(file_path)
        sound.play()
        pygame.time.delay(int(sound.get_length() * 1000))
    except pygame.error as e:
        print(f"Error playing the WAV file: {e}")
    finally:
        pygame.quit()

# For unit Testing
# def text_to_speech(text, out_path):
#     # Construct the command to invoke the TTS engine
#     command = ["tts", "--text", text, "--out_path", out_path]

#     try:
#         # Run the command and capture the output
#         subprocess.run(command, check=True, shell=True)
#         subprocess.run(command)
#         print(f"TTS successfully generated at {out_path}")
#     except subprocess.CalledProcessError as e:
#         print(f"Error running TTS command: {e}")

# For Efficiency
def text_to_speech(text, out_path):
    # Construct the command to invoke the TTS engine
    command = ["tts", "--text", text, "--out_path", out_path]
    subprocess.run(command)


# Expect to receive a tolerance level from front end
def compare_poses(ref_pose_path, user_pose_path, tolerance=10):

    print(f"Current Tolerance Angle: {tolerance}")
    if user_pose_path is None or ref_pose_path is None:
        print("Error: Please provide paths for user_pose and ref_pose.")
        # return

    try:
        # Load and parse the JSON files
        with open(user_pose_path, 'r') as file:
            input_data = json.load(file)

        with open(ref_pose_path, 'r') as file:
            local_data = json.load(file)

    except FileNotFoundError:
        print("Error: One or both of the provided JSON files not found.")
        # return

    # Extract the keypoints from the JSON data
    input_keypoints = input_data["people"][0]["pose_keypoints_2d"]

    local_keypoints = local_data["people"][0]["pose_keypoints_2d"]

    lhand_keypoints = input_data["people"][0]["hand_left_keypoints_2d"]

    rhand_keypoints = input_data["people"][0]["hand_right_keypoints_2d"]

    local_lhand_keypoints = local_data["people"][0]["hand_left_keypoints_2d"]

    local_rhand_keypoints = local_data["people"][0]["hand_right_keypoints_2d"]


    # Ensure the two lists have the same length
    if len(input_keypoints) != len(local_keypoints):
        print("Keypoint lists have different lengths.")
    
    if len(lhand_keypoints) != len(local_lhand_keypoints):
        print("Left Hand Keypoint lists have different lengths.")
    
    if len(rhand_keypoints) != len(local_rhand_keypoints):
        print("Right Hand Keypoint lists have different lengths.")


    # Reshape the arrays to have shape (n, 3), where n is the number of keypoints
    input_keypoints = np.array(input_keypoints).reshape(-1, 3)
    local_keypoints = np.array(local_keypoints).reshape(-1, 3)
    lhand_keypoints = np.array(lhand_keypoints).reshape(-1, 3)
    rhand_keypoints = np.array(rhand_keypoints).reshape(-1, 3)
    local_lhand_keypoints = np.array(local_lhand_keypoints).reshape(-1, 3)
    local_rhand_keypoints = np.array(local_rhand_keypoints).reshape(-1, 3)

    # Remove confidence intervals prior to comparison
    input_keypoints = input_keypoints[:, :2]
    local_keypoints = local_keypoints[:, :2]
    lhand_keypoints = lhand_keypoints[:, :2]
    rhand_keypoints = rhand_keypoints[:, :2]
    local_lhand_keypoints = local_lhand_keypoints[:, :2]
    local_rhand_keypoints = local_rhand_keypoints[:, :2]

    name_list=["Head", "Right_Shoulder", "Right_Upperarm", "Right_Lowerarm", "Left_Shoulder", "Left_Upperarm",
               "Left_Lowerarm", "Upper_Body", "Left_Waist", "Left_Thigh", "Left_Calf", "Right_Waist",
                "Right_Thigh", "Right_Calf", "Left_Feet", "Right_Feet"]

    body_parts = {
        'head': ['Head'],
        'upperbody': ['Upper_Body', 'Left_Waist', 'Right_Waist'], 
        'arms': ['Right_Shoulder', 'Left_Shoulder', 'Right_Upperarm', 'Right_Lowerarm', 'Left_Upperarm', 'Left_Lowerarm'],
        'legs': ['Left_Calf', 'Right_Calf', 'Left_Thigh', 'Right_Thigh'],
        'feet': ['Left_Feet', 'Right_Feet']
} 
    # Defining all user inputs
    head_torso = input_keypoints[0] - input_keypoints[1]
    torso_rarmtop = input_keypoints[1] - input_keypoints[2]
    rarmtop_rarmmid = input_keypoints[2] - input_keypoints[3]
    rarmmid_rhand = input_keypoints[3] - input_keypoints[4]
    torso_larmtop = input_keypoints[1] - input_keypoints[5]
    larmtop_larmmid = input_keypoints[5] - input_keypoints[6]
    larmmid_lhand = input_keypoints[6] - input_keypoints[7]
    torso_waist = input_keypoints[1] - input_keypoints[8]
    waist_llegtop = input_keypoints[8] - input_keypoints[9]
    llegtop_llegmid = input_keypoints[9] - input_keypoints[10]
    llegmid_lfoot = input_keypoints[10] - input_keypoints[11]
    waist_rlegtop = input_keypoints[8] - input_keypoints[12]
    rlegtop_rlegmid = input_keypoints[12] - input_keypoints[13]
    rlegmid_rfoot = input_keypoints[13] - input_keypoints[14]
    lfoot = input_keypoints[14] - input_keypoints[19]
    rfoot = input_keypoints[11] - input_keypoints[22]
    
    input_set = [
        tuple(head_torso), tuple(torso_rarmtop), tuple(rarmtop_rarmmid),
        tuple(rarmmid_rhand), tuple(torso_larmtop), tuple(larmtop_larmmid),
        tuple(larmmid_lhand), tuple(torso_waist), tuple(waist_llegtop),
        tuple(llegtop_llegmid), tuple(llegmid_lfoot), tuple(waist_rlegtop),
        tuple(rlegtop_rlegmid), tuple(rlegmid_rfoot), tuple(lfoot), tuple(rfoot)
    ]

    # Define All Local Inputs
    head_torsol = local_keypoints[0] - local_keypoints[1]
    torso_rarmtopl = local_keypoints[1] - local_keypoints[2]
    rarmtop_rarmmidl = local_keypoints[2] - local_keypoints[3]
    rarmmid_rhandl = local_keypoints[3] - local_keypoints[4]
    torso_larmtopl = local_keypoints[1] - local_keypoints[5]
    larmtop_larmmidl = local_keypoints[5] - local_keypoints[6]
    larmmid_lhandl = local_keypoints[6] - local_keypoints[7]
    torso_waistl = local_keypoints[1] - local_keypoints[8]
    waist_llegtopl = local_keypoints[8] - local_keypoints[9]
    llegtop_llegmidl = local_keypoints[9] - local_keypoints[10]
    llegmid_lfootl = local_keypoints[10] - local_keypoints[11]
    waist_rlegtopl = local_keypoints[8] - local_keypoints[12]
    rlegtop_rlegmidl = local_keypoints[12] - local_keypoints[13]
    rlegmid_rfootl = local_keypoints[13] - local_keypoints[14]
    lfootl = local_keypoints[14] - local_keypoints[19]
    rfootl = local_keypoints[11] - local_keypoints[22]

    userisfist_left = False
    userisfist_right = False
    localisfist_left = False
    localisfist_right = False  

    local_set = [
        tuple(head_torsol), tuple(torso_rarmtopl), tuple(rarmtop_rarmmidl),
        tuple(rarmmid_rhandl), tuple(torso_larmtopl), tuple(larmtop_larmmidl),
        tuple(larmmid_lhandl), tuple(torso_waistl), tuple(waist_llegtopl),
        tuple(llegtop_llegmidl), tuple(llegmid_lfootl), tuple(waist_rlegtopl),
        tuple(rlegtop_rlegmidl), tuple(rlegmid_rfootl), tuple(lfootl), tuple(rfootl)
    ]

    lhand_set = [
        tuple(lhand_keypoints[0]), tuple(lhand_keypoints[9]), tuple(lhand_keypoints[10]),
        tuple(lhand_keypoints[11]), tuple(lhand_keypoints[12])
    ]

    rhand_set = [
        tuple(rhand_keypoints[0]), tuple(rhand_keypoints[9]), tuple(rhand_keypoints[10]),
        tuple(rhand_keypoints[11]), tuple(rhand_keypoints[12])
    ]

    local_lhand_set = [
        tuple(local_lhand_keypoints[0]), tuple(local_lhand_keypoints[9]), tuple(local_lhand_keypoints[10]),
        tuple(local_lhand_keypoints[11]), tuple(local_lhand_keypoints[12])
    ]

    local_rhand_set = [
        tuple(local_rhand_keypoints[0]), tuple(local_rhand_keypoints[9]), tuple(local_rhand_keypoints[10]),
        tuple(local_rhand_keypoints[11]), tuple(local_rhand_keypoints[12])
    ]

    # User input
    lhand_x = [keypoint[0] for keypoint in lhand_set]
    lhand_y = [keypoint[1] for keypoint in lhand_set]

    rhand_x = [keypoint[0] for keypoint in rhand_set]
    rhand_y = [keypoint[1] for keypoint in rhand_set]

    # Checking for a general trend in x coordinates for both sets
    lnot_fist_x = all(x <= y for x, y in zip(lhand_x, lhand_x[1:])) or all(x >= y for x, y in zip(lhand_x, lhand_x[1:]))
    rnot_fist_x = all(x <= y for x, y in zip(rhand_x, rhand_x[1:])) or all(x >= y for x, y in zip(rhand_x, rhand_x[1:]))

    # Checking for a general trend in y coordinates for both sets
    lnot_fist_y = all(x <= y for x, y in zip(lhand_y, lhand_y[1:])) or all(x >= y for x, y in zip(lhand_y, lhand_y[1:]))
    rnot_fist_y = all(x <= y for x, y in zip(rhand_y, rhand_y[1:])) or all(x >= y for x, y in zip(rhand_y, rhand_y[1:]))

    luser_result = [lnot_fist_x, lnot_fist_y]
    ruser_result = [rnot_fist_x, rnot_fist_y]

    if all(luser_result):
        userisfist_left = False
    else:
        userisfist_left = True
    
    if all(ruser_result):
        userisfist_right = False
    else:
        userisfist_right = True

    # Reference Handpose
    lhand_xl = [keypoint[0] for keypoint in local_lhand_set]
    lhand_yl = [keypoint[1] for keypoint in local_lhand_set]

    rhand_xl = [keypoint[0] for keypoint in local_rhand_set]
    rhand_yl = [keypoint[1] for keypoint in local_rhand_set]

    # Checking for a general trend in x coordinates for both sets
    lnot_fist_xl = all(x <= y for x, y in zip(lhand_xl, lhand_xl[1:])) or all(x >= y for x, y in zip(lhand_xl, lhand_xl[1:]))
    rnot_fist_xl = all(x <= y for x, y in zip(rhand_xl, rhand_xl[1:])) or all(x >= y for x, y in zip(rhand_xl, rhand_xl[1:]))

    # Checking for a general trend in y coordinates for both sets
    lnot_fist_yl = all(x <= y for x, y in zip(lhand_yl, lhand_yl[1:])) or all(x >= y for x, y in zip(lhand_yl, lhand_yl[1:]))
    rnot_fist_yl = all(x <= y for x, y in zip(rhand_yl, rhand_yl[1:])) or all(x >= y for x, y in zip(rhand_yl, rhand_yl[1:]))

    luser_resultl = [lnot_fist_xl, lnot_fist_yl]
    ruser_resultl = [rnot_fist_xl, rnot_fist_yl]

    if all(luser_resultl):
        localisfist_left = False
    else:
        localisfist_left = True
    
    if all(ruser_resultl):
        localisfist_right = False
    else:
        localisfist_right = True

    if localisfist_right != userisfist_right:
        print("Check your Right Hand Posture!")
    if localisfist_left != userisfist_left:
        print("Check your Left Hand Posture!")
    # TODO: Voice output here or return to frontend to showcase issue

    similarities = []
    angles_in_degrees = []

    for vector1, vector2 in zip(input_set, local_set):
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)

        # Check if either norm is zero or very close to zero
        if norm1 < 1e-10 or norm2 < 1e-10:
            # Handle the case where the magnitude is too small
            similarity = 0.0
            angle_degrees = 0.0
        else:
            similarity = np.dot(vector1, vector2) / (norm1 * norm2)
            similarity = max(-1, min(1, similarity))
            angle = np.arccos(similarity)
            # angle_degrees = np.degrees(angle)

        similarities.append(similarity)
        angles_in_degrees.append(angle)

    average_similarity = np.mean(similarities) # TODO: Pending for changes, valuing lower body part more?
    print(f"Score: {average_similarity*100}")

    if average_similarity > 0.9:
        message = "Great, you made it!"
        out_path = "D:/Workspace/Taichine/Voice/Good.wav" # TODO: Designated Folder/Flash Storage
        print(f"Great, you made it! You mastered the pose.")
        text_to_speech(message, out_path)
        play_wav_file(out_path)
        sys.exit()

    max_degrees = 0
    error_list = []

    for i, (similarity, angle_degrees) in enumerate(zip(similarities, angles_in_degrees)):
        if (angle_degrees * 180 / math.pi) < tolerance:
            continue
        else:
            if math.isnan(angle_degrees):
                print(f"Angle (in degrees) between {name_list[i]} and reference pose: 0.0000")
            else:
                print(f"Angle (in degrees) between {name_list[i]} and reference pose: {(angle_degrees * 180 / math.pi):.4f}")
                error_list.append(name_list[i])
        if angle_degrees > max_degrees:
            max_degrees = angle_degrees
            max_i = i
    degrees = max(angles_in_degrees) * 180 / math.pi
    worst_angle = round(degrees)

    # TODO: Instruction wording, use error_list and body_list above to give different instructions
    # 'head', 'upperbody', 'arms', 'legs', 'feet'
    # Direction Calculation for Arms
    # if (x1 < x2 and y1 < y2) or (x1 > x2, y1 > y2):
    #     if deltax < deltay: print("Moveup")
    #     else: print("Movedown")
    # else:
    #     if deltax < deltay: print("Movedown")
    #     else: print("Moveup")

    message = f"Your worst angle is {worst_angle} degrees at {name_list[max_i]}"
    # TODO: Idea: Feet->Leg/Thigh->Upper Body(Torso)->Arms, Instructions should be issued from this sequence
    # TODO: Leg Instructions need to be compared to the an axis line representing center of body (Joint angle + Ref Angle)
    out_path = "D:/Workspace/Taichine/Voice/Angle.wav"
    # text_to_speech(message, out_path)
    # play_wav_file(out_path)
    return

# TODO @ Hongzhe: Need to implement file search for different references
def backend_process ():
    parseImageFromPath("user_input\\", "user_pose_data\\")

    # Compare the poses
    reference_path = "SampleOutput\\1\\1_keypoints.json"
    user_path = "user_pose_data\\user_keypoints.json"

    print("Comparing User data with " + reference_path)

    return compare_poses(reference_path, user_path)

# Backend Submodule test code
# Main function takes in the user image path and a reference name, compare the two poses and provide output
# if __name__ == "__main__":
#     # Parse cmdline input for test purpose
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--user_image", required = True)
#     parser.add_argument("--reference_pose", required = True)
#     parser.add_argument("--tolerance", type=int, default=10, help="Tolerance value")

#     args = parser.parse_args()

#     # Process user image with OpenPose
#     parseImageFromPath(args.user_image, "user_pose_data\\")

#     # Compare the poses
#     reference_path = "SampleOutput\\1\\" + args.reference_pose + "_keypoints.json"
#     user_path = "user_pose_data\\user_keypoints.json"

#     print("Comparing User data with " + reference_path)

#     compare_poses(reference_path, user_path)

# TODO: Instruction wording/formatting. Feet on the ground? How you word to lower your thigh?
# Angle between thigh and a reference vertical line, either to expand your legs or tighten them additional to the relative angle.

# TODO: Feedbacks of posture analysis, limb specific instructions.
# Raise/Lower {Left/Right} {limb name}, by {x} degrees. I have all limbs labelled so should be fine.
# TODO: Priortize lower body part, assigning weight for different body parts
# TODO: Should be a tolerance threshold for angle? How much should it be?
