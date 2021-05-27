from PIL import Image
import numpy as np
import subprocess

output_width = 21  # Width of output gif, measured in sussy crewmates
twerk_frame_count = 6  # 0.png to 5.png

# Load twerk frames 🥵
twerk_frames = []
twerk_frames_data = []  # Image as numpy array, pre-calculated for performance
for i in range(6):
    img = Image.open(f"{i}.png").convert("RGBA")
    twerk_frames.append(img)
    twerk_frames_data.append(np.array(img))

# Get dimensions of first twerk frame. Assume all frames have same dimensions
twerk_width, twerk_height = twerk_frames[0].size

# Get image to sussify!
input_image = Image.open("input.png").convert("RGB")
input_width, input_height = input_image.size

# Height of output gif (in crewmates)
output_height = int(output_width * (input_height / input_width) * (twerk_width / twerk_height))

for frame_number in range(twerk_frame_count):
    print("Sussying frame #", frame_number)

    # Create blank canvas
    background = Image.new(mode="RGBA", size=(output_width*twerk_width, output_height*twerk_height))
    for y in range(output_height):
        for x in range(output_width):
            # Get rgb values from input image (basically nearest neighbour interpolation)
            r, g, b = input_image.getpixel((int(x / output_width * input_width), int(y / output_height * input_height)))

            # Grab that twerk data we calculated earlier
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

print("Converting sussy frames to sussy gif")
# Convert sussied frames to gif. PIL has a built-in method to save gifs but
# it has dithering which looks sus, so we use ffmpeg with dither=none
subprocess.call('./ffmpeg -f image2 -i sussified_%d.png -filter_complex "[0:v] scale=sws_dither=none:,split [a][b];[a] palettegen=max_colors=255:stats_mode=single [p];[b][p] paletteuse=dither=none" -r 20 -y -hide_banner -loglevel error sussified.gif')

# lamkas a cute