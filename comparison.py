import json
import numpy as np
import math
import sys
import argparse
# import pyttsx3
# sys.path.append("..")
from OpenPoseInter import parseImageFromPath

# Globals
# Define a fixed vertical vector pointing straight up
vertical_vector = np.array([0, 1])
horizontal_vector = np.array([1, 0])


# Expect to receive a tolerance level from front end
# Return formatting:
# {
#   Bool PosePoss
#   ndarray ReferenceCoordinates
#   ndarray UserCoordinates
#   List LimbCorrect
#   List UserAngles
#   List ReferenceAngles
# }
def compare_poses(ref_pose_path, user_pose_path, tolerance=10):

    output_list = []
    pose_pass = False
    name_list=["Head", "Right Shoulder", "Right Upperarm", "Right Lowerarm", "Left Shoulder", "Left Upperarm",
               "Left Lowerarm", "Torso", "Right Waist", "Left Waist", "Right Thigh", "Right Calf", 
               "Left Thigh", "Left Calf", "Left Feet", "Right Feet"]

    body_parts = {
        'head': ['Head'],
        'upperbody': ['Torso', 'Left Waist', 'Right Waist'], 
        'arms': ['Right Shoulder', 'Left Shoulder', 'Right Upperarm', 'Right Lowerarm', 'Left Upperarm', 'Left Lowerarm'],
        'legs': ['Left Calf', 'Right Calf', 'Left Thigh', 'Right Thigh'],
        'feet': ['Left Feet', 'Right Feet']
}
    
    print(f"Current Tolerance Angle: {tolerance}")
    if user_pose_path is None or ref_pose_path is None:
        print("Error: Please provide paths for user_pose and ref_pose.")
        return

    try:
        # Load and parse the JSON files
        with open(user_pose_path, 'r') as file:
            input_data = json.load(file)

        with open(ref_pose_path, 'r') as file:
            local_data = json.load(file)

    except FileNotFoundError:
        print("Error: One or both of the provided JSON files not found.")
        return

    # Multiple People Implementation
    # Method: No matter how incomplete your posture is, I always just evaluate the one
    # that is the most similar, given that the user is attempting the posture
    # Extract the keypoints from the JSON data

    # Case: No Person in Frame
    if not input_data["people"]:
        print("Error: No person found")
        # return
 
    best_score = 0
    best_person = 0
    # Person list will be consist of cur_person in the loop below
    # cur_person is a list formatted as following:
    # [i, [input_keypoints], [missing_jointname], ["right" , "left"], [input_quads_final], 
    # average_similarity, [angles_in_rads]]
    person_list = []
    for i in range(len(input_data["people"])):
        cur_person = []
        cur_person.append(i)
        # Extract the keypoints from the JSON data
        input_keypoints = input_data["people"][i]["pose_keypoints_2d"]

        local_keypoints = local_data["people"][0]["pose_keypoints_2d"]

        lhand_keypoints = input_data["people"][i]["hand_left_keypoints_2d"]

        rhand_keypoints = input_data["people"][i]["hand_right_keypoints_2d"]

        local_lhand_keypoints = local_data["people"][0]["hand_left_keypoints_2d"]

        local_rhand_keypoints = local_data["people"][0]["hand_right_keypoints_2d"]

        # Ensure the two lists have the same length
        # if len(input_keypoints) != len(local_keypoints):
        #     raise ValueError("Keypoint lists have different lengths.")
        
        # if len(lhand_keypoints) != len(local_lhand_keypoints):
        #     raise ValueError("Left Hand Keypoint lists have different lengths.")
        
        # if len(rhand_keypoints) != len(local_rhand_keypoints):
        #     raise ValueError("Right Hand Keypoint lists have different lengths.")

        # Reshape the arrays to have shape (n, 3)
        input_keypoints = np.array(input_keypoints).reshape(-1, 3)
        input_keypoints = input_keypoints[:, :2] # Remove confidence interval
        cur_person.append(input_keypoints)  


        # List Missing joints and match missing points with names
        missing_jointname = [] # This could be returned to frontend
        missing_joints = [j for j, sublist in enumerate(input_keypoints) if np.array_equal(sublist, np.array([0, 0]))]
        for joint in missing_joints:
            if joint in range(len(name_list)):
                # Probably do a dict
                missing_jointname.append(name_list[joint])
            elif joint == 19:
                missing_jointname.append(name_list[14])
            elif joint == 22:
                missing_jointname.append(name_list[15])
        # if missing_jointname != []:
        # print(missing_jointname) # DEBUG
        cur_person.append(missing_jointname)
        # TODO: Say something about missing bodypart: Include your body in frame
            # Integration TODO: return the list if non-empty? TBD

        local_keypoints = np.array(local_keypoints).reshape(-1, 3)
        lhand_keypoints = np.array(lhand_keypoints).reshape(-1, 3)
        rhand_keypoints = np.array(rhand_keypoints).reshape(-1, 3)
        local_lhand_keypoints = np.array(local_lhand_keypoints).reshape(-1, 3)
        local_rhand_keypoints = np.array(local_rhand_keypoints).reshape(-1, 3)

        # Remove confidence intervals prior to comparison
        local_keypoints = local_keypoints[:, :2]
        lhand_keypoints = lhand_keypoints[:, :2]
        rhand_keypoints = rhand_keypoints[:, :2]
        local_lhand_keypoints = local_lhand_keypoints[:, :2]
        local_rhand_keypoints = local_rhand_keypoints[:, :2]


        # Defining all user inputs
        head_torso = input_keypoints[0] - input_keypoints[1]
        torso_rarmtop = input_keypoints[1] - input_keypoints[2]
        rarmtop_rarmmid = input_keypoints[2] - input_keypoints[3]
        rarmmid_rhand = input_keypoints[3] - input_keypoints[4]
        torso_larmtop = input_keypoints[1] - input_keypoints[5]
        larmtop_larmmid = input_keypoints[5] - input_keypoints[6]
        larmmid_lhand = input_keypoints[6] - input_keypoints[7]
        torso_waist = input_keypoints[1] - input_keypoints[8]
        waist_rlegtop = input_keypoints[8] - input_keypoints[9]
        waist_llegtop = input_keypoints[8] - input_keypoints[12]
        rlegtop_rlegmid = input_keypoints[9] - input_keypoints[10]
        rlegmid_rfoot = input_keypoints[10] - input_keypoints[11]
        llegtop_llegmid = input_keypoints[12] - input_keypoints[13]
        llegmid_lfoot = input_keypoints[13] - input_keypoints[14]
        lfoot = input_keypoints[14] - input_keypoints[19]
        rfoot = input_keypoints[11] - input_keypoints[22]
        
        input_set = [
            tuple(head_torso), tuple(torso_rarmtop), tuple(rarmtop_rarmmid),
            tuple(rarmmid_rhand), tuple(torso_larmtop), tuple(larmtop_larmmid),
            tuple(larmmid_lhand), tuple(torso_waist), tuple(waist_rlegtop),
            tuple(waist_llegtop), tuple(rlegtop_rlegmid), tuple(rlegmid_rfoot),
            tuple(llegtop_llegmid), tuple(llegmid_lfoot), tuple(lfoot), tuple(rfoot)
        ]
        x_coor_input = []
        y_coor_input = []
        for ele in input_set:
            x_coor_input.append(ele[0])
            y_coor_input.append(ele[1])
        x_coor_input = np.array(x_coor_input)
        y_coor_input = np.array(y_coor_input)

        # Define All Local Inputs
        head_torsol = local_keypoints[0] - local_keypoints[1] # Head
        torso_rarmtopl = local_keypoints[1] - local_keypoints[2] # Shoulder (Arm)
        rarmtop_rarmmidl = local_keypoints[2] - local_keypoints[3] # Arm
        rarmmid_rhandl = local_keypoints[3] - local_keypoints[4] # Arm
        torso_larmtopl = local_keypoints[1] - local_keypoints[5] # Shoulder (Arm)
        larmtop_larmmidl = local_keypoints[5] - local_keypoints[6] # Arm
        larmmid_lhandl = local_keypoints[6] - local_keypoints[7] # Arm
        torso_waistl = local_keypoints[1] - local_keypoints[8] # Upper Body
        waist_rlegtopl = local_keypoints[8] - local_keypoints[9] # Waist (Leg)
        waist_llegtopl = local_keypoints[8] - local_keypoints[12] # Waist (Leg)
        rlegtop_rlegmidl = local_keypoints[9] - local_keypoints[10] # Leg
        rlegmid_rfootl = local_keypoints[10] - local_keypoints[11] # Leg
        llegtop_llegmidl = local_keypoints[12] - local_keypoints[13] # Leg
        llegmid_lfootl = local_keypoints[13] - local_keypoints[14] # Leg
        lfootl = local_keypoints[14] - local_keypoints[19] # Feet (Leg)
        rfootl = local_keypoints[11] - local_keypoints[22] # Feet (Leg)

        userisfist_left = False
        userisfist_right = False
        localisfist_left = False
        localisfist_right = False  

        local_set = [
            tuple(head_torsol), tuple(torso_rarmtopl), tuple(rarmtop_rarmmidl),
            tuple(rarmmid_rhandl), tuple(torso_larmtopl), tuple(larmtop_larmmidl),
            tuple(larmmid_lhandl), tuple(torso_waistl), tuple(waist_rlegtopl),
            tuple(waist_llegtopl), tuple(rlegtop_rlegmidl), tuple(rlegmid_rfootl),
            tuple(llegtop_llegmidl), tuple(llegmid_lfootl), tuple(lfootl), tuple(rfootl)
        ]
        x_coor_local = []
        y_coor_local = []
        for ele in local_set:
            x_coor_local.append(ele[0])
            y_coor_local.append(ele[1])
        x_coor_local = np.array(x_coor_local)
        y_coor_local = np.array(y_coor_local)

################ Starting hand Comparison ##################
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

        if localisfist_right != userisfist_right and localisfist_left != userisfist_left:
            cur_person.append(["right", "left"])
        elif localisfist_right != userisfist_right:
            cur_person.append(["right"])
            message = "Check your Right Hand Posture!"
            print(message)
            pyttsx3.speak(message)
        elif localisfist_left != userisfist_left:
            cur_person.append(["left"])
            message = "Check your Left Hand Posture!"
            print(message)
            pyttsx3.speak(message)
        else:
            cur_person.append([])
################## End of Hand Comparison #########################

        # Body part comparison
        similarities = []
        angles_in_rads = []

        # The angle from np.arctan2 will be the angle between the vector and negative x-axis
        local_quads_final = []
        input_quads_final = []
        local_quads = np.arctan2(y_coor_local, x_coor_local) * 180 / np.pi # Conversion from rads
        input_quads = np.arctan2(y_coor_input, x_coor_input) * 180 / np.pi # ^^
        for deg in local_quads:
            if deg < 0:
                deg = -180 - deg
            else:
                deg = 180 - deg
            local_quads_final.append(round(deg, 4))
        for deg2 in input_quads:
            if deg2 < 0:
                deg2 = -180 - deg2
            else:
                deg2 = 180 - deg2
            input_quads_final.append(round(deg2, 4))
        cur_person.append(input_quads_final)
        # TODO: For skeleton drawing, grab the local_quads_final and input_quads_final above

        for vector1, vector2 in zip(input_set, local_set):
            norm1 = np.linalg.norm(vector1)
            norm2 = np.linalg.norm(vector2)

            # Check if either norm is zero or very close to zero
            if norm1 < 1e-10 or norm2 < 1e-10:
                # Handle the case where the magnitude is too small
                similarity = 0.0
                angle = 0.0
            else:
                similarity = np.dot(vector1, vector2) / (norm1 * norm2)
                similarity = max(-1, min(1, similarity))
                angle = np.arccos(similarity) # Radians

            similarities.append(similarity)
            angles_in_rads.append(angle)

        average_similarity = np.mean(similarities) # TODO: Pending for changes, valuing lower body part more?
        print(f"Score: {average_similarity*100}")
        cur_person.append(average_similarity)
        cur_person.append(angles_in_rads)
        person_list.append(cur_person)
        if average_similarity > best_score:
            best_score = average_similarity
            best_person = i

    # print(best_score)
    # print(person_list)

    limb_checklist = [] # Passing to Frontend for limb correctness drawing
    max_degrees = 0
    error_namelist = []
    error_angle = []
    sentence_list = []

    # Uncomment the following to check outputs without full body in frame
    # if len(person_list[best_person][1]) != 0:
    #     best_radians = []
    # else:
    best_radians = person_list[best_person][-1] # Return this angle list to front end for skeleton drawing
    # print(best_radians)
    # if len(best_radians) == 0:
    #     out_path = "D:/Workspace/Taichine/Voice/Bad.wav" # TODO: Designated Folder/Flash Storage
    #     message = "Adjust your posture to include full body in frame"
    #     print(message)
    #     text_to_speech(message, out_path)
    #     play_wav_file(out_path)
    # Comment out this branch above to test without full body images
    # else:
    # TODO: Check torso and head first before checking rest of the body parts according to Taichi expert
    # (head_torsol, torso_waistl), (head_torso, torso_waist)
    # [0] and [7] compare the rads -> tolerance, give errors if those are wrong

    word_choice = [["inwards", "outwards"], ["upwards", "downwards"]]
    angle_differences = [(a - b + 180) % 360 - 180 for a, b in zip(person_list[best_person][4], local_quads_final)]
    # print(angle_differences)
    # for rad in best_radians:
    #     passed_angle.append(rad * 180 / math.pi)
        # Conversion to Degrees
    for k, (similarity, angle_degrees) in enumerate(zip(similarities, angle_differences)):
        if abs(angle_degrees) < tolerance:
            limb_checklist.append(True)
            continue
        else:
            if math.isnan(angle_degrees):
                continue
                # print(f"Angle (in degrees) between {name_list[k]} and reference pose: 0.0000")
            else:
                if k in [1, 4, 8, 9]: # Representing Shoulder and Waist, Up and Down would be make more sense on those joints
                    m = 1
                else:
                    m = 0
                if angle_degrees > 0: # Comparing to decide whether user have overdone or underdone the pose
                    n = 0
                else:
                    n = 1
                message = f"Turn your {name_list[k]} {word_choice[m][n]} by {abs(round(angle_degrees))} degrees"
                sentence_list.append(message)
                limb_checklist.append(False)
                error_namelist.append(name_list[k])
                error_angle.append(angle_degrees)
            if angle_degrees > max_degrees:
                max_degrees = angle_degrees         

    if not error_namelist: # All poses pass == Error list empty
        message = "Great, you made it!"
        print("Great, you made it! You mastered the pose.")
        pyttsx3.speak(message)
        pose_pass = True
    else:
        # worst_angle = round(max(angle_differences, key=abs))
        # message = f"Your worst angle is {worst_angle} degrees at {name_list[max_k]}"
        print(sentence_list)
        message = sentence_list[-1]
        pyttsx3.speak(message)

    # person_list = [[cur_person], [cur_person], ...]
    # cur_person = [i, [input_keypoints], [missing_jointname], ["right" , "left"], [input_quads_final], 
    # average_similarity, [angles_in_rads]]
    output_list.append(pose_pass)
    output_list.append(local_keypoints)
    output_list.append(person_list[best_person][1])
    output_list.append(limb_checklist)
    output_list.append(person_list[best_person][4]) # User Angles
    output_list.append(local_quads_final) # Ref Angles
    output_list.append(person_list[best_person][5]) # Score

    print(output_list)
    return output_list


    # For instructions: Take difference in joint angles and direction,
    # instruct them

    # TODO: Instruction wording, derive from angles with direction, and give
    # corresponding angles
    # 'head', 'upperbody', 'arms', 'legs', 'feet'
    # Direction Calculation for Arms
    # if (x1 < x2 and y1 < y2) or (x1 > x2, y1 > y2):
    #     if deltax < deltay: print("Moveup")
    #     else: print("Movedown")
    # else:
    #     if deltax < deltay: print("Movedown")
    #     else: print("Moveup")


# TODO @ Hongzhe: Need to implement file search for different references
def backend_process (mode, pose_name, image_name, tolerance):
    # Process the user
    parseImageFromPath("user_input\\", "user_pose_data\\")

    # Get reference
    image_index = image_name.split(".png")[0]
    reference_path = "SampleOutput\\" + str(int(pose_name.split("-")[0])) + "\\" + image_index + "_keypoints.json"
    if mode == "custom": #TODO @ Hongzhe: where are custom poses
        reference_path = "custom_pose\\" + pose_name + "\\" + image_index + "_keypoints.json"
    user_path = "user_pose_data\\user_keypoints.json"

    print("Comparing User data with " + reference_path, tolerance)

    # Compare and generate output
    return compare_poses(reference_path, user_path, tolerance)

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
#     # TODO: Implement a loop through grab the image until it appears. ?Will it work?
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
