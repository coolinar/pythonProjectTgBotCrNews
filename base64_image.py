import base64

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

WELCOME_IMAGE_BASE64 = encode_image_to_base64('C:\\Users\\Admin\\Downloads\\Zerocoder\\img_tgbot\\img_bot.jpeg')
print(WELCOME_IMAGE_BASE64)  # Выводит строку Base64

