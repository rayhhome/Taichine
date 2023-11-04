import json
import numpy as np
import math
import sys
import subprocess


def text_to_speech(text, out_path):
    # Construct the command to invoke the TTS engine
    command = ["tts", "--text", text, "--out_path", out_path]

    try:
        # Run the command and capture the output
        subprocess.run(command, check=True, shell=True)
        print(f"TTS successfully generated at {out_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running TTS command: {e}")

# Expect to receive a tolerance level from front end
def main(tolerance=10, ref_pose_path, user_pose_path):

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

    # Extract the keypoints from the JSON data
    input_keypoints = input_data["people"][0]["pose_keypoints_2d"]

    local_keypoints = local_data["people"][0]["pose_keypoints_2d"]

    # Ensure the two lists have the same length
    if len(input_keypoints) != len(local_keypoints):
        raise ValueError("Keypoint lists have different lengths.")


    # Reshape the arrays to have shape (n, 3), where n is the number of keypoints
    input_keypoints = np.array(input_keypoints).reshape(-1, 3)
    local_keypoints = np.array(local_keypoints).reshape(-1, 3)

    # Remove confidence intervals prior to comparison
    input_keypoints = input_keypoints[:, :2]
    local_keypoints = local_keypoints[:, :2]

    # Only want keypoints 0-14, first 15 entries
    input_keypoints = input_keypoints[:15]
    local_keypoints = local_keypoints[:15]

    # name_list=[Head, Right_Shoulder, Right_Upperarm, Right_Lowerarm, Left_Shoulder, Left_Upperarm, Left_Lowerarm, Upper_Body, Left_Waist,
    #        Left_Thigh, Left_Calf, Right_Waist, Right_Thigh, Right_Calf]
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

    input_set = {
        tuple(head_torso), tuple(torso_rarmtop), tuple(rarmtop_rarmmid),
        tuple(rarmmid_rhand), tuple(torso_larmtop), tuple(larmtop_larmmid),
        tuple(larmmid_lhand), tuple(torso_waist), tuple(waist_llegtop),
        tuple(llegtop_llegmid), tuple(llegmid_lfoot), tuple(waist_rlegtop),
        tuple(rlegtop_rlegmid), tuple(rlegmid_rfoot)
    }

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

    local_set = {
        tuple(head_torsol), tuple(torso_rarmtopl), tuple(rarmtop_rarmmidl),
        tuple(rarmmid_rhandl), tuple(torso_larmtopl), tuple(larmtop_larmmidl),
        tuple(larmmid_lhandl), tuple(torso_waistl), tuple(waist_llegtopl),
        tuple(llegtop_llegmidl), tuple(llegmid_lfootl), tuple(waist_rlegtopl),
        tuple(rlegtop_rlegmidl), tuple(rlegmid_rfootl)
    }

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
            angle_degrees = np.degrees(angle)

        similarities.append(similarity)
        angles_in_degrees.append(angle_degrees)
        
    average_similarity = np.mean(similarities) # TODO: Pending for changes, valuing lower body part more?
    print(f"Score: {average_similarity*100}")

    if average_similarity > 0.9:
        message = "Great, you made it!"
        out_path = "D:/Workspace/Taichine/Voice/Good.wav"
        # TODO: Make the playing of the file
        print(f"Great, you made it!")
        text_to_speech(message, out_path)
        sys.exit()


    for i, (similarity, angle_degrees) in enumerate(zip(similarities, angles_in_degrees)):
        if angle_degrees < tolerance:
            break
        else:
            if math.isnan(angle_degrees):
                print(f"Angle (in degrees) between input_set[{i}] and local_set[{i}]: 0.0000")
            else:
                print(f"Angle (in degrees) between input_set[{i}] and local_set[{i}]: {angle_degrees:.4f}")

if __name__ == "__main__":
    # Provide the 'tolerance' value as a command-line argument, it defaults to 10 degrees if not provided.
    if len(sys.argv) > 1:
        try:
            tolerance = float(sys.argv[1])
            main(tolerance)
        except ValueError:
            print("Tolerance must be a valid number.")
    else:
        main()  # Default tolerance of 0


# TODO: Change this, this is currently a debug output
# Ask Eric for more dataseet and further analysis

# TODO: Feedbacks of posture analysis, limb specific instructions.
# Raise/Lower {Left/Right} {limb name}, by {x} degrees. I have all limbs labelled so should be fine.
# How do I derive from the consine similarity to actual angles? Should be a correlation I could follow.
# Invoke TTS engine to produce .wav file in designated folder,
# Then use the script to play the generated instruction.
# Storage? Do I wipe all the saved .wav files after the session? After each posture (in my mind)?
# TODO: Priortize lower body part, assigning weight for different body parts
# TODO: Should be a tolerance threshold for angle? How much should it be?
