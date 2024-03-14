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

login_images_dict = {}


print("loading login images ...")
# Assuming you have a file named 'data.json'
with open('./data/login_image.json', 'r') as file:
	login_images_dict = json.load(file)
print("loading openCV model ...")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
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



def resize_and_paste(dest_img, src_img, position):
	# Open the destination and source images

	# Calculate the size needed for the destination image
	required_width = max(dest_img.width, position[0] + src_img.width)
	required_height = max(dest_img.height, position[1] + src_img.height)
	
	offset_x = max(0, -position[0])
	offset_y = max(0, -position[1])

	required_width += offset_x
	required_height += offset_y
	


	# Check if the destination image needs to be resized
	if dest_img.width < required_width or dest_img.height < required_height:
		# Resize the destination image
		new_dest_img = Image.new('RGBA', (required_width, required_height), (0, 0, 0, 0))
		new_dest_img.paste(dest_img, (offset_x, offset_y))
		dest_img = new_dest_img

	
	position = (position[0] + offset_x, position[1] + offset_y)
	# Paste the source image onto the destination image
	dest_img.paste(src_img, position, src_img if src_img.mode == 'RGBA' else None)
	
	return dest_img


def linkify_image(input_image, image_a_coller_path):
	# Appliquer rembg pour supprimer l'arrière-plan
	print("removing background ...")
	output_image = remove(input_image)
	print("background removed")
	
	# Convertir l'image résultante en un objet PIL Image
	image = output_image

	# Charger l'image à coller
	image_a_coller_original = Image.open(image_a_coller_path)

	# Charger le modèle de détection de visages d'OpenCV
	print("detecting faces ...")
	image_cv = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
	
	# Détecter les visages dans l'image
	faces = face_cascade.detectMultiScale(cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY), 1.1, 4)
	print(f"detected {len(faces)} faces")

	for (x, y, w, h) in faces:
		# Redimensionner l'image à coller pour qu'elle corresponde à la largeur du visage
		# Tout en conservant les proportions. On peut ajouter une marge si nécessaire.
		scale_factor = w / image_a_coller_original.width * 2.5
		new_width = int(image_a_coller_original.width * scale_factor)
		new_height = int(image_a_coller_original.height * scale_factor)
		image_a_coller = image_a_coller_original.resize((new_width, new_height), Image.Resampling.LANCZOS)
		
		# Calculer le point d'ancrage pour positionner l'image à coller sur la tête
		# On place le bas du bonnet juste au-dessus des yeux, typiquement à 1/4 de la hauteur du visage au-dessus des yeux.
		anchor_x = x + (w - new_width) // 2  # Centre le bonnet sur le visage
		anchor_y = y - new_height // 2#+ h // 1 - new_height    # Ajuste la hauteur du bonnet
		
		# # S'assurer que le bonnet ne dépasse pas de l'image de fond
		# if anchor_x < 0: anchor_x = 0
		# if anchor_y < 0: anchor_y = 0
		# if anchor_x + new_width > image.width: anchor_x = image.width - new_width
		# if anchor_y + new_height > image.height: anchor_y = image.height - new_height

			
		# Redimensionner l'image à coller pour qu'elle corresponde à la largeur du visage
		# ... [le code pour redimensionner est identique]

		# Créer un masque transparent pour la zone où les cheveux doivent être supprimés
		mask = Image.new('RGBA', image.size, (0, 0, 0, 0))
		mask_draw = ImageDraw.Draw(mask)

		
		alpha = image.split()[3]
		alpha_mask_draw = ImageDraw.Draw(alpha)
		
		# Dessiner un rectangle transparent sur la partie supérieure du visage
		alpha_mask_draw.rectangle([(0, 0), (image.size[1], anchor_y + new_height/ 3 *1.9)], fill=0)
		# alpha_mask_draw.rectangle([(x, 0), (x + w, anchor_y + new_height/ 3 *1.9)], fill=0)
	
		# Mettre à jour la couche alpha de l'image originale
		image.putalpha(alpha)
		# image.paste(image_a_coller, (anchor_x, anchor_y), image_a_coller)
		image = resize_and_paste(image, image_a_coller, (anchor_x, anchor_y))


	# Sauvegarder l'image résultante en format PNG pour conserver la transparence
	# image.save(output_path, format='PNG')
	# print(f"image saved to {output_path}")
	return image


def linkify_user(login):
	print("fetching image for " + login + " ...")
	image = get_login_image(login)
	if image is None:
		return None
	print("image fetched")
	result = linkify_image(image, './data/bonnet_alone.png')
	return result