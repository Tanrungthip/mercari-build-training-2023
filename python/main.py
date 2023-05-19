import os
import logging
import pathlib
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

# db_path = "./db/mercari.sqlite3"
db_path = pathlib.Path(__file__).parent.resolve() / "db" / "mercari.sqlite3"

def create_table(conn: sqlite3.Connection):
    table = [
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            image_name TEXT NOT NULL,
            FOREIGN KEY(category_id) REFERENCES category(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """
    ]
    try:
        c = conn.cursor()
        for statement in table:
            c.execute(statement)
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")

conn = sqlite3.connect(db_path)
create_table(conn)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    logger.info(f"Receive item: {name}, category: {category}")
    # Hash image file, a string representing the SHA-256 image data
    image_hash = hashlib.sha256(image.file.read()).hexdigest()
    image_filename = f"{image_hash}.jpg"

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id FROM category WHERE name=?", (category,))
    category_id = c.fetchone()

    if category_id is None:
        c.execute("INSERT INTO category (name) VALUES (?)", (category,))
        conn.commit()
        # Fetch the new category id
        c.execute("SELECT id FROM category WHERE name=?", (category,))
        category_id = c.fetchone()
    # Create ITEM
    item = [name, category_id[0], image_hash]
    c.execute("INSERT INTO items (name, category_id, image_name) VALUES (?, ?, ?)", item)
    conn.commit()
    conn.close()
    return {"message": f"item received: {name}, category: {category}, image: {image_filename}"}

# Define a route for the "/items" URL with a GET method
@app.get("/items")
def get_items():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT items.id, items.name, category.name, items.image_name\
        from items INNER JOIN category ON items.category_id = category.id")
    items = c.fetchall()
    conn.close()
    return items
# this return [[1,"coffee","beverage","af1bb8dd235ef9e9bd9a509cec4c2b650d75080287f1bee6d12646c53d28ef83"],[2,"kiwi","fruit","af1bb8dd235ef9e9bd9a509cec4c2b650d75080287f1bee6d12646c53d28ef83"]

@app.get("/items/{item_id}")
def get_item_id(item_id: int):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT items.id, items.name, category.name, items.image_name\
        from items INNER JOIN category ON items.category_id = category.id")
    items = c.fetchall()
    conn.commit()
    conn.close()
    return items[item_id - 1]
# this return [2,"kiwi","fruit","af1bb8dd235ef9e9bd9a509cec4c2b650d75080287f1bee6d12646c53d28ef83"]%

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
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"SELECT * from items WHERE name = '{keyword}'")
    search_results = c.fetchall()
    return search_results
# this return [[4,"tesla",4,"af1bb8dd235ef9e9bd9a509cec4c2b650d75080287f1bee6d12646c53d28ef83"]]%
