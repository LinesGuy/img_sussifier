from PIL import Image
import numpy as np
import subprocess

width = 50
imgs = [Image.open(f"{n}.png").convert("RGBA") for n in range(6)]
cell_width = imgs[0].size[0]
cell_height = imgs[0].size[1]

im = Image.open("input.png")
height = int((width * im.size[1]) / im.size[0] * 75 / 65)
scaled = im.resize((width, height), Image.NEAREST).convert("RGB")
scaled.save("scaled.png")

frames = []
for frame in range(6):
    background = Image.new(mode="RGB", size=(width*cell_width, height*cell_height))
    for y in range(height):
        for x in range(width):
            r, g, b = scaled.getpixel((x, y))
            data = np.array(imgs[(x-y+frame) % len(imgs)])
            red, green, blue, alpha = data.T
            color_1 = (red == 214) & (green == 224) & (blue == 240)
            color_2 = (red == 131) & (green == 148) & (blue == 191)
            data[..., :-1][color_1.T] = (r, g, b)
            data[..., :-1][color_2.T] = (int(r*2/3), int(g*2/3), int(b*2/3))
            im3 = Image.fromarray(data)
            #im3.show()
            #input()
            background.paste(im3, (x*cell_width, y*cell_height))
    frames.append(background)
[f.save(f"out_{n}.png") for n, f in enumerate(frames)]
# NO TRANSPARENCY:
subprocess.call('ffmpeg -f image2 -i out_%d.png -filter_complex "[0:v] scale=sws_dither=none:,split [a][b];[a] palettegen=max_colors=255:stats_mode=single [p];[b][p] paletteuse=dither=none" -r 20 -y test.gif')
# TRANSPARENCY (removes any black pixels)
#subprocess.call('ffmpeg -f image2 -i out_%d.png -filter_complex "[0:v]chromakey=0x000000,scale=sws_dither=none:,split [a][b];[a] palettegen=max_colors=255:stats_mode=single [p];[b][p] paletteuse=dither=none" -r 20 -y test.gif')

#frames[0].save("out.gif", save_all=True, append_images=[frames[1], frames[2], frames[3], frames[4], frames[5]], loop=0, optimize=True)

#background.show()
