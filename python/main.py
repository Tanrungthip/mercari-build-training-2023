import os
import logging
import pathlib
import json
import hashlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

data_base = "mercari.sqlite3"


@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    logger.info(f"Receive item: {name}, category: {category}")
    # Hash image file, a string representing the SHA-256 image data
    image_hash = hashlib.sha256(image.file.read()).hexdigest()
    image_filename = f"{image_hash}.jpg"
    # Save image file
    image_path = images / image_filename
    with open(image_path, "wb") as file:
        file.write(image.file.read())

    # Add item into items db
    conn = sqlite3.connect('data_base')
    c = conn.cursor()
    c.execute("INSERT INTO items (name, category, image_name) VALUES (?, ?, ?)", (name, category, image_filename))
    # Commit / Close command
    conn.commit()
    item_id = c.lastrowid
    conn.close()
    return {"id": item_id, "name": name, "category": category, "image_filename": image_filename}

    # # Open items.json file
    # with open('items.json', 'r') as file:
    #     items = json.load(file)
    # # Add new item to the items list
    # items['items'].append({"name": name, "category": category, "image_filename" : image_filename})
    # # Updated items back to file
    # with open('items.json', 'w') as file:
    #     json.dump(items, file)
    # return {"message": f"item received: {name}, category: {category}, image: {image_filename}"}

@app.get("/items")
def get_items():
    conn = sqlite3.connect('data_base')
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = [{"id": row[0], "name": row[1], "category": row[2], "image_filename": row[3]} for row in c.fetchall()]
    conn.close()
    return {"items": items}

    # # Open the items.json file
    # with open('items.json', 'r') as f:
    #     items = json.load(f)
    # return items

@app.get("/items/{item_id}")
def get_item_id(item_id: int):
    conn = sqlite3.connect('data_base')
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE id=?", (item_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return {"id": row[0], "name": row[1], "category": row[2], "image_filename": row[3]}
    else:
        raise HTTPException(status_code=404, detail="Item not found")

    # with open('items.json','r') as file:
    #     items = json.load(file)

    # return items['items'][item_id]

@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)

@app.get("/search")
def search_items(keyword: str):
    conn = sqlite3.connect(data_base)
    c = conn.cursor()
    c.execute(f"SELECT * FROM items WHERE name = '{keyword}'")
    items = c.fetchall()
    conn.commit()
    conn.close()
    return items
