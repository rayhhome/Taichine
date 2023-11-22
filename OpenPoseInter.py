import os

def parseImageFromPath (image_folder, output_folder):
    input_path = image_folder
    output_path = output_folder

    cmd = ".\\bin\OpenPoseDemo.exe --write_json " + output_path + " --image_dir " + input_path + " --write_images " + output_path + " --hand"
    print(cmd)
    os.system(cmd)
    print('oopsy')

# C:\Users\eric3\OneDrive\Desktop\CMU Assignment\openpose\TaichiPosesHi\2
# for i in range(24):
#     parseImageFromPath ("TaichiPosesHi\\" + str(i + 1), "SampleOutput\\" + str(i + 1))