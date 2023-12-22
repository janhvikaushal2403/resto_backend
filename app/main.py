import os
import secrets
import base64
import json
from PIL import Image
from io import BytesIO

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import schemas

from .database import engine
from . import models
from .routes import rest, groups, menu, orders

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

static_url = 'localhost:8000'
static_images_path = './static/images/'

app.mount('/static', StaticFiles(directory="static"), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to the Restraunt"}


app.include_router(rest.router)
app.include_router(groups.router)
app.include_router(groups.router2)
app.include_router(groups.router3)
app.include_router(menu.router)
app.include_router(orders.router)


@app.post('/upload/images/{v}')
async def upload_images(v: str, data: schemas.ImageUpload):

    FILEPATH = './static/images/'

    # Extract information from the JSON payload
    filename = data.filename
    extension = data.extension
    image_data = data.image_data

    if not all([filename, extension, image_data]):
        return {
            'status': "200",
            'msg': "Invalid JSON payload. Make sure to include filename, extension, and image_data.",
        }

    # Check if the extension is valid
    if extension not in ['png', 'jpg', 'jpeg']:
        return {
            'status': "200",
            'msg': "Can't upload image, not in the correct format",
        }

    token = secrets.token_hex(10)
    generated_name = FILEPATH + token + '.' + extension

    # Decode the base64-encoded image data
    try:
        image_content = base64.b64decode(image_data)
    except Exception as e:
        return {
            'status': "200",
            'msg': f"Error decoding base64 image data: {str(e)}",
        }

    with open(generated_name, "wb") as file:
        file.write(image_content)

    # Resize the image if it's an item
    if v == 'item':
        img = Image.open(generated_name)
        img = img.resize(size=(200, 200))
        img.save(generated_name)

    print(generated_name)
    file_url = static_url + generated_name[1:]

    return {
        'status': "200",
        'msg': "Successfully posted image",
        'data': {
            'filename': token + '.' + extension,
            # 'filename': generated_name[1:],
            'file_url': file_url
        }
    }


# @app.post('/upload/images/{v}')
# async def upload_images(v: str, image: UploadFile = File(...)):

#     FILEPATH = './static/images/'
#     filename = image.filename
#     extension = filename.split('.')[1]

#     if extension not in ['png', 'jpg','jpeg']:
#         return{
#             'status': "200",
#             'msg': "can't upload image, not in correct format",
#         }

#     token = secrets.token_hex(10)
#     generated_name = FILEPATH + token + '.' + extension
#     file_content = await image.read()

#     with open(generated_name, "wb") as file:
#         file.write(file_content)

#     # pillow
#     if v == 'item':
#         img = Image.open(generated_name)
#         img = img.resize(size=(200,200))
#         img.save(generated_name)

#     file.close()
#     print(generated_name)
#     file_url = static_url + generated_name[1:]

#     return{
#         'status': "200",
#         'msg': "successfully posted image",
#         'data': {
#             'filename' : generated_name[1:],
#             'file_url' : file_url
#         }
#     }
# localhost:8000/static/images/b003dab0f1d14ff712a3.png
@app.get("/images/{image_id}")
def get_image(image_id: str):
    # Adjust the path to your image storage
    image_path = static_images_path + image_id
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/jpeg/")
    else:
        return {"detail": "Image not found"}
