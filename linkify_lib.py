import cv2
from PIL import Image
from rembg import remove
from io import BytesIO
import numpy
from PIL import ImageDraw
from PIL import ImageOps

import json
import requests
from io import BytesIO
import asyncio
import os

login_images_dict = {}
hats_images_path_list = []


print("loading login images ...")
# Assuming you have a file named 'data.json'
with open('./data/login_image.json', 'r') as file:
	login_images_dict = json.load(file)
print("loading openCV model ...")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
print("done")


print("discovering hats images ...")
for filename in os.listdir('./data/hats'):
	if filename.endswith(".png"):
		hats_images_path_list.append(os.path.join('./data/hats', filename))
	else:
		continue
print("done")


def get_login_image_link(login) -> str:
	return login_images_dict.get(login, None)


def get_login_image(login) -> Image:
	link = get_login_image_link(login)
	if link is None:
		return None
	response = requests.get(link)
	img = Image.open(BytesIO(response.content))
	return img



def resize_and_paste(dest_img, src_img, position, show_debug_lines=False):

	bbox = src_img.getbbox()
	src_img = src_img.crop(bbox)

	position = (position[0] + bbox[0], position[1] + bbox[1])

	required_width = max(dest_img.width, position[0] + src_img.width)
	required_height = max(dest_img.height, position[1] + src_img.height)
	

	offset_x = max(0, -position[0])
	offset_y = max(0, -position[1])

	required_width += offset_x
	required_height += offset_y
	
	if dest_img.width < required_width or dest_img.height < required_height:
		new_dest_img = Image.new('RGBA', (required_width, required_height), 0)
		if (show_debug_lines):
			ImageDraw.Draw(new_dest_img).rectangle([(0, 0), (required_width, required_height)], (128, 0, 128, 128))
		new_dest_img.paste(dest_img, (offset_x, offset_y))
		dest_img = new_dest_img

	position = (position[0] + offset_x, position[1] + offset_y)	
	dest_img.paste(src_img, position, src_img if src_img.mode == 'RGBA' else None)
	
	return dest_img


def linkify_image(input_image, hat_image, hat_face_width, hat_face_height, show_debug_lines=False):
	# Appliquer rembg pour supprimer l'arrière-plan
	print("removing background ...")
	output_image = remove(input_image)
	print("background removed")
	
	# Convertir l'image résultante en un objet PIL Image
	image = output_image

	print("detecting faces ...")
	image_cv = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
	
	faces = face_cascade.detectMultiScale(cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY), 1.1, 4)
	print(f"detected {len(faces)} faces")

	bigest_width = 0
	for (x, y, w, h) in faces:
		bigest_width = max(w, bigest_width)

	for (x, y, w, h) in faces:
		if (bigest_width != w):
			continue
		scale_factor = w / hat_face_width
		new_width = int(hat_image.width * scale_factor)
		new_height = int(hat_image.height * scale_factor)
		modified_hat_image = hat_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
		
		anchor_x = x + (w - new_width) // 2
		anchor_y = y - new_height // 2
		
		mask = Image.new('RGBA', image.size, (0, 0, 0, 0))
		mask_draw = ImageDraw.Draw(mask)

		
		alpha = image.split()[3]
		alpha_mask_draw = ImageDraw.Draw(alpha)
		
		alpha_mask_draw.rectangle([(0, 0), (image.size[1], y + hat_face_height * scale_factor)], fill=0)
		image.putalpha(alpha)
		if (show_debug_lines):
			ImageDraw.Draw(image).rectangle([(x, y), (x + w, y + h)], outline=(0, 255, 0, 255))
			ImageDraw.Draw(image).rectangle([(x, 0), (x + w, y)], outline=(255, 0, 0, 255))
		
		image = resize_and_paste(image, modified_hat_image, (anchor_x, anchor_y), show_debug_lines)
	return image


def generate_id_from_string(input_string, range):
    hash_value = hash(input_string)
    id_in_range = hash_value % range
    return id_in_range


def get_hat(login, show_debug_lines=False):
	hat_path = hats_images_path_list[generate_id_from_string(login, len(hats_images_path_list))]
	hat_image = Image.open(hat_path).rotate(20, expand=True)
	displacement_height = -300
	hat_image = hat_image.crop((0, displacement_height, hat_image.width, hat_image.height + displacement_height))
	if (show_debug_lines):
		ImageDraw.Draw(hat_image).rectangle([(hat_image.width // 2 - 10, hat_image.height // 2 - 10), (hat_image.width // 2 + 10, hat_image.height // 2 + 10)], fill=(0, 0, 255, 255))
	return hat_image
	

def linkify_user(login, flip_hat=False , show_debug_lines=False):
	print("fetching image for " + login + " ...")
	image = get_login_image(login)
	if image is None:
		return None
	print("image fetched")
	hat_image = get_hat(login, show_debug_lines)
	if flip_hat:
		hat_image = ImageOps.mirror(hat_image)
	result = linkify_image(image, hat_image, 1175, 120, show_debug_lines)
	return result