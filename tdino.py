# HEY THERE! STOP RIGHT HERE! First, read how to read this document:
# This is an explenation. Read code as if it is normal text and try to understand how and what it does before continuing.

from blessed import Terminal
import random
import time

term = Terminal()

# First, we create the landscape itself. The "dino" stays stationary on the x axis, while the floor moves below him. 
# The floor can have cacti of 2 types: short and long.
# First, we define a arrays of our terminals width where each array element represents a char in our console.

console_width = term.width
console_height = term.height
floor_params = [None] * console_width

# Now, that this is done, we want to fill the floor parameters with some values to represent the cacti "growing" on the floor
# For this, we want to define the probability with which cacti grows on the char x. To do this, we create an array with
# The correct proportions of empty floor chars and each of the cacti types. Here, the probability that the floor char will be
# empty, is 90%.  

probabilities = [0] * 96 + [1] * 2 + [2] * 2
cooldown_gap = 20
since_last_cactus = 0

def next_floor_char():
    global since_last_cactus

    value = probabilities[random.randint(0, 99)]

    # Too soon after the last cactus? Force empty floor.
    if value != 0 and since_last_cactus < cooldown_gap:
        value = 0

    if value != 0:
        since_last_cactus = 0
    else:
        since_last_cactus += 1

    return value


# So, with the proportions and cooldown gaps defined we now fill the floor parameter list randomly. We fill the array
# With output of the next_floor_char() function that keeps track of the cooldown gap so that a jump over the cacti
# stays possible

for i in range(len(floor_params)):
    floor_params[i] = next_floor_char()

# Now, it would be pretty unfortunate if the dino spawns inside or directly in from of a cactus. Lets clear 25 chars of room for him.

for i in range(0, 25):
    floor_params[i] = 0

# We now have all the data necessary to generate the floor. The floor will look like this:
#                        0
#      0                 0
#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
# With the 0s being the cacti. These are the types 1 and 2 from left to right. 0 is the floor without any cacti.
# Okay, with that defined we now generate the floors of the appropriate length for our cacti. 

def generate_floor():
    global console_height, floor_params
    #Block 1
    out = term.move_xy(0, console_height - 3)

    for i in range(len(floor_params)):
        if floor_params[i] == 2:
            out += "0"
        else:
            out += " "
    #Block 2
    out += term.move_xy(0, console_height - 2)

    for i in range(len(floor_params)):
        if floor_params[i] == 1 or floor_params[i] == 2:
            out += "0"
        else:
            out += " "
    #Block 3
    out += term.move_xy(0, console_height - 1)

    for i in range(len(floor_params)):
            out += "°"

    return "".join(out)


# Oh dang it, a pretty long function. Lets dissect it carefully. You see, the funcion consists of 3 blocks, each
# beginning with an out... and ending with a for loop. Basically, each of them draws one row of the floor like this:
# 
# floor_params: 00000010000000000002000000000 (array representation)
# Block 1     :                    0
# Block 2     :       0            0
# Block 3     : °°°°°°°°°°°°°°°°°°°°°°°°°°°°°
#
# The function adds the outputs together on top of each other with a moving cursor by using term.move_xy(x, y)
# and returns it after joining it with an empty string.

# Well done! Currently, the floor is static and not moving. However, we do want that to change. For that we do the following thing:
# We make the array behave like a queue. Imagine a queue of people standing at a waffle stand. The one leaves and the other gets 
# into the queue. The same should happen with our array.        
#                                
# __CLI____________________-_x           __CLI____________________-_x           __CLI____________________-_x
# |                          |           |                          |           |                          | 
# |                          |     3     |                          |     3     |                          |
# |               v      v   |     ->    |            v      v      |     ->    |         v      v         |   
# |00000102000010020000001000|           |00102000010020000001000010|           |02000010020000001000010002|
# |__________________________|           |__________________________|           |__________________________|
#
# Pay attention to the first 1 from the right. The floor parameters array is just moving left more and more. And with that new elements
# are inserted into the array from the left. This is what we are going to implement in the next function.

def redefine_floor():
    global floor_params
    floor_params.pop(0)
    floor_params.append(next_floor_char())

# Let us analyze the function step by step. First, we declare the floor_params variable as global to access it from inside our function.
# Then, we "pop" the first element of our array. It gets removed. Lastly, we append a new element to our floor_params array with a new, 
# random next_floor_char.

# WOW! The floor is finished! Now we can get over to building the dinosaur itself. This is gonna be our dino: "╷^╷°`"
# I know, it doesnt look like a dinosaur, but with a little imagination... there he is! Lets call him "Triccy".
# 
# Now, we just need a function for Triccy. It should display him at certain coordinates x and y so that we can give commands to move him
# later.

def move_triccy(x, y):
    return "".join(term.move_xy(x, y) + "╷^╷°`")

# Now, we just need a function to make him jump. 

triccy_jump_position = 0
triccy_jumped = False
triccy_finished_jump = True
triccy_up_counter = 0

def jump_triccy():
    global triccy_jump_position, triccy_jumped, triccy_finished_jump, triccy_up_counter

    if triccy_jump_position < 3 and not triccy_jumped:
        triccy_jump_position += 1

    elif triccy_jump_position == 3 and not triccy_jumped and triccy_up_counter != 3:
        triccy_up_counter += 1

    elif triccy_jump_position == 3 and not triccy_jumped and triccy_up_counter == 3:
        triccy_jumped = True
        triccy_up_counter = 0

    elif triccy_jumped and triccy_jump_position > 0:
        triccy_jump_position -= 1

    elif triccy_jump_position == 0 and triccy_jumped:
        triccy_jumped = False
        triccy_finished_jump = True

# Now we have defined some new if-else blocks. They give Triccy his flight trajectory. But dont worry, the terminal doesn't posess an air 
# resistance. We want Triccy to travel up wards one char at a time up to 3 chars above ground, hold there for 3 seconds and then fall back 
# down with the same rate. Try to follow what happens with Triccy during all these loops. triccy_jump_position describes his height above ground.

# Now for the collision detector! Triccy always stands at x = 3 and is 5 chars wide, so he covers the columns 3 to 7.
# We look at what is growing on the floor in exactly these columns.

triccy_x = 3
triccy_width = 5

def check_collision():
    # Look at every floor column that is under Triccy
    for i in range(triccy_x, triccy_x + triccy_width):
        cactus = floor_params[i]   # 0 = empty, 1 = short, 2 = long

        # Triccy is safe if he is higher than the cactus is tall
        if cactus != 0 and triccy_jump_position < cactus:
            return True

    return False


# And now.... Drumrolls! Comes the heart of our programm! Its the while loop. After putting the terminal into fullscreen and hiding the cursor,
# we activate the while loop and read the key pressed. Then we assemble the whole terminal with all its debug, floor and, of course, Triccy.
# Before printing, we ask check_collision() whether Triccy is touching a cactus. If he is, we add "GAME OVER" to the frame, print it,
# wait for any key to be pressed and break out of the loop, which ends the game. If not, we print the frame as normal and check whether
# Triccy should jump at that point. Then, we redraw the floor as previously defined and make the software wait a bit so that it wont get 
# too fast for the player. Then, we check for the keys pressed.

with term.fullscreen(), term.hidden_cursor(), term.cbreak():
    while True:
        key = term.inkey(timeout=0.1)
        if check_collision():
            toprint += term.move_xy(console_width // 2 - 4, console_height // 2) + "GAME OVER"
            print(toprint, end="", flush=True)
        else:
            toprint = term.clear()
            toprint += term.move_xy(0, 0) + str(floor_params)
            toprint += term.move_xy(0, 9) + "Current height: " + str(triccy_jump_position)
            toprint += term.move_xy(22, 9) + "since_last_cactus:  " + str(since_last_cactus)
            
            toprint += generate_floor()
            toprint += move_triccy(3, console_height-2-triccy_jump_position)

            print(toprint, end="", flush=True)

            if triccy_finished_jump == False:
                jump_triccy()
                
            
            redefine_floor()

        #time.sleep(0.01)

        if key == 'q':
            break
        if key == " ":
            triccy_finished_jump = False



# Crafted with <3 by Mark Scharonow for Hack Club