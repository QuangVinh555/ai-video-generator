from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip, CompositeVideoClip

img = Image.new('RGBA', (1080, 200), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("assets/fonts/Montserrat-Black.ttf", 60)
except:
    font = ImageFont.load_default()

draw.text((100, 50), "TESTING SUBTITLES", font=font, fill=(255, 255, 0, 255), stroke_width=6, stroke_fill=(0,0,0,255))
img.save("test_text.png")

img_array = np.array(img)
color = img_array[:, :, :3]
mask = img_array[:, :, 3] / 255.0

txt_clip = ImageClip(color).set_mask(ImageClip(mask, ismask=True))
txt_clip = txt_clip.set_duration(2).set_position(('center', 'center'))

bg = ImageClip(np.zeros((1920, 1080, 3))).set_duration(2)
comp = CompositeVideoClip([bg, txt_clip], size=(1080, 1920))
comp.save_frame("test_comp.png", t=1)
