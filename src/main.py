from fastapi import FastAPI, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import cv2
import numpy as np
from jwt_auth import JWTBearer

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = load_model("./src/model/hybridModel_03.h5")

article_classes = {
    0: "Backpacks",
    1: "Caps",
    2: "Casual Shoes",
    3: "Dresses",
    4: "Flats",
    5: "Flip Flops",
    6: "Formal Shoes",
    7: "Heels",
    8: "Jackets",
    9: "Jeans",
    10: "Sandals",
    11: "Shirts",
    12: "Skirts",
    13: "Sports Shoes",
    14: "Sweaters",
    15: "Sweatshirts",
    16: "Tops",
    17: "Trousers",
    18: "Tshirts",
}

usage_classes = {0: "Casual", 1: "Formal", 2: "Sports"}


@app.post("/classify", dependencies=[Depends(JWTBearer())])
async def classify(file: UploadFile):
    nparr = np.frombuffer(await file.read(), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (224, 224))
    image = preprocess_input(image)
    final_array = np.expand_dims(image, axis=0)

    predictions = model.predict(final_array)
    article = np.argmax(predictions[0], axis=-1)
    usage = np.argmax(predictions[1], axis=-1)

    article_name = article_classes[article[0]]
    usage_name = usage_classes[usage[0]]

    return {"message": "success", "data": {"type": article_name, "usage": usage_name}}
