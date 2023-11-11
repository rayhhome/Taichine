from os import rename, listdir

taichi_name = [
  "Commence form",
  "Parting wild horse's mane (3 times)",
  "White crane spreads its wings",
  "Brush knee and press (3 times)",
  "Play the lute",
  "Repulse the monkey (4 times)",
  "Grasp the sparrow's tail (left and right)",
  "Single whip",
  "Wave hands like clouds",
  "Single whip (other side)",
  "High pat on horse",
  "Right heel kick",
  "Strike opponent's ears with fists",
  "Turn around, left heel kick",
  "Snake creeps down",
  "Golden rooster standing on left leg",
  "Snake creeps down",
  "Golden rooster standing on right leg",
  "Fair lady works the shuttles (right and left)",
  "Needles at sea bottom",
  "Fan through back",
  "Turn around, block, parry and punch",
  "Withdraw and push",
  "Cross hands and close form"
]

all_poses = listdir('./poses')
all_poses.sort()

i = 0
for name in all_poses:
  if i == 24:
    break
  rename('poses/' + name, 'poses/' + name + ' - ' + taichi_name[int(name.split('.')[0]) - 1])

print(all_poses)
