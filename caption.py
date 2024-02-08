import base64
import requests
import os
import sys
import argparse
# OpenAI API Key
api_key = os.environ.get("OPENAI_API_KEY")

# Overwrite files or only generate captions for images that don't have captions
overwrite = False

# The extension for the caption file
caption_extension = "txt"



if api_key is None:
	print("Error: OPENAI_API_KEY environment variable not set")
	sys.exit(1)

# Parse the arguments
parser = argparse.ArgumentParser(description="Generate captions for a folder of images")
parser.add_argument("keyword", help="The token/keyword for the session")
parser.add_argument("image_folder", help="The folder containing the images")

# Optional arguments

parser.add_argument("--ext", help="The extension for the caption file", default=".txt")
args = parser.parse_args()

keyword = args.keyword
image_folder = args.image_folder


# 


# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')



def generate_caption(image_path):
  # Getting the base64 string
	base64_image = encode_image(image_path)
	headers = {
	"Content-Type": "application/json",
	"Authorization": f"Bearer {api_key}"
	}

	payload = {
	"model": "gpt-4-vision-preview",
	"messages": [
		{
		"role": "user",
		"content": [
			{
			"type": "text",
			"text": '''Classify image with precision using session keywords for object/subject captions for Stable Diffusion. Begin captions with the session keyword, focusing on actions, clothing, photo style, and scenery. Avoid putting a semicolon after the session keyword. Add descriptions of the photo itself such as "selfie" or "full body shot". If the photo does have many details or is very blurry mention that it is low quality. Refer to the subject by the keyword. Instead of "KEYWORD woman" just say "KEYWORD". Avoid artistic interpretation, text, and meta commentary. The session keyword is "{keyword}" '''.format(keyword=keyword)
			},
			{
			"type": "image_url",
			"image_url": {
				"url": f"data:image/jpeg;base64,{base64_image}"
			}
			}
		]
		}
	],
	"max_tokens": 300
	}
	response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
	# Get the response
	response = response.json()
	return response['choices'][0]['message']['content']



# Grab a folder of images and generate captions for each image

# Ensure the folder exists
if not os.path.exists(image_folder):
	print(f"Error: {image_folder} does not exist")
	quit()

# Check if caption files already exist, if so, ask the user if they want to overwrite them
caption_files = [file for file in os.listdir(image_folder) if file.endswith(caption_extension)]
if len(caption_files) > 0:
	print(f"Warning: {len(caption_files)} caption files already exist in {image_folder}")
	overwrite = input("Do you want to overwrite them? (y/n): ")
	
	if overwrite.lower() != "y":
		overwrite = False
	else:
		overwrite = True
		# Delete the caption files
		for file in caption_files:
			os.remove(os.path.join(image_folder, file))


images = []
valid_extensions = [".jpg", ".jpeg", ".png"]

for file in os.listdir(image_folder):
	# Check if the file is an image
	if file.endswith(tuple(valid_extensions)):
		images.append(os.path.join(image_folder, file))

if len(images) == 0:
	print(f"No images found in {image_folder}")
	quit()

print(f"Found {len(images)} images")

for image in images:
	# Check if the caption file already exists
	if not overwrite:
		caption_file = os.path.splitext(image)[0] + "." + caption_extension
		if os.path.exists(caption_file):
			print(f"Caption file already exists for {image}")
			continue
	caption = generate_caption(image)
	# Print the caption
	print (f"Caption for {image}: {caption}")
	# Write the caption to a file
	# Get the filename without the extension
	filename = os.path.splitext(image)[0]
	# Write the caption to a file
	with open(filename +"."+ caption_extension, 'w') as f:
		f.write(caption)
	

