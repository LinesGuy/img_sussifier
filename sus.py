from PIL import Image
import numpy as np
import subprocess
import os

output_width = 21  # Measured in crewmates
try:
    output_width = int(input("Enter width of output image in crewmates [default=21]: "))
except ValueError:
    print("Invalid input, using default width of 21.")
if output_width >= 75:
    input("That is a VERY large width, output is measured in crewmates (75x65 pixels each) NOT raw pixels. Press CTRL+C to cancel or enter to continue (this may take a long time)")

nearest_neighbour = True
nn_input = input('Use nearest neighbor? (Keep enabled for flags, disable to smooth the output if image is "noisy") [y/n, default=y]: ').lower()
if nn_input == "n" or nn_input == "no":
    nearest_neighbour = False
elif nn_input == "y" or nn_input == "yes":
    pass
else:
    print("Invalid input, using default value of yes")

# Load twerk frames
twerk_frames = []
twerk_frames_data = []  # Image as numpy array, pre-calculated for performance
print("Loading twerk frames... ", end="")
for i in range(6):
    try:
        img = Image.open(f"twerk_imgs/{i}.png").convert("RGBA")
    except Exception as e:
        print(f"Error loading twerk frames! Filename = {i}.png")
        print("Probably you renamed the twerk_imgs folder or deleted it.")
        print(e)
        input()
        exit()
    twerk_frames.append(img)
    twerk_frames_data.append(np.array(img))
print("Done!")

# Get dimensions of first twerk frame. Assume all frames have same dimensions
twerk_width, twerk_height = twerk_frames[0].size

# Get image to sussify
print("Opening input.png... ", end="")
try:
    input_image = Image.open("input.png").convert("RGB")
except Exception as e:
    print("Error loading input.png, make sure it's in the same directory as this script.")
    print(e)
    input()
    exit()
print("Done!")
input_width, input_height = input_image.size

# Height of output gif (in crewmates)
output_height = int(output_width * (input_height / input_width) * (twerk_width / twerk_height))

# Width, height of output in pixels
output_px = (int(output_width * twerk_width), int(output_height * twerk_height))

# Scale image to number of crewmates, so each crewmate gets one color
if nearest_neighbour:
    input_image_scaled = input_image.resize((output_width, output_height), Image.NEAREST)
else:
    input_image_scaled = input_image.resize((output_width, output_height))

for frame_number in range(6):
    print(f"Processing frame #{frame_number}... ", end="")

    # Create blank canvas
    background = Image.new(mode="RGBA", size=output_px)
    for y in range(output_height):
        for x in range(output_width):
            r, g, b = input_image_scaled.getpixel((x, y))

            # Grab the twerk data we calculated earlier
            # (x - y + frame_number) is the animation frame index,
            # we use the position and frame number as offsets to produce the wave-like effect
            sussified_frame_data = np.copy(twerk_frames_data[(x - y + frame_number) % len(twerk_frames)])
            red, green, blue, alpha = sussified_frame_data.T
            # Replace all pixels with colour (214,224,240) with the input image colour at that location
            color_1 = (red == 214) & (green == 224) & (blue == 240)
            sussified_frame_data[..., :-1][color_1.T] = (r, g, b)  # thx stackoverflow
            # Repeat with colour (131,148,191) but use two thirds of the input image colour to get a darker colour
            color_2 = (red == 131) & (green == 148) & (blue == 191)
            sussified_frame_data[..., :-1][color_2.T] = (int(r*2/3), int(g*2/3), int(b*2/3))

            # Convert sussy frame data back to sussy frame
            sussified_frame = Image.fromarray(sussified_frame_data)

            # Slap said frame onto the background 
            background.paste(sussified_frame, (x * twerk_width, y * twerk_height))
    background.save(f"sussified_{frame_number}.png")
    print("Done!")

print("Saving as .gif... ", end="")
# Convert sussied frames to gif. PIL has a built-in method to save gifs but
# it has dithering which looks sus, so we use ffmpeg with dither=none
try:
    subprocess.call('ffmpeg -f image2 -i sussified_%d.png -filter_complex "[0:v] scale=sws_dither=none:,split [a][b];[a] palettegen=max_colors=255:stats_mode=single [p];[b][p] paletteuse=dither=none" -r 20 -y -hide_banner -loglevel error sussified.gif')
except Exception as e:
    print("Error saving as .gif, make sure ffmpeg is installed system-wide or ffmpeg.exe is in the same directory as this script.")
    print(e)
    input()
    exit()
print("Done!")

# Remove temp files
print("Removing temporary files... ", end="")
for frame_number in range(6):
    os.remove(f"sussified_{frame_number}.png")
print("Done!")

# lamkas a cute