import aiomysql
import asyncio
import clip
import torch
from PIL import Image
import os

# Replace with your actual database configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'your_username',
    'password': 'your_password',
    'db': 'your_database',
    'charset': 'utf8mb4',
    'autocommit': True
}

# Replace with your actual table name and column names
TABLE_NAME = 'image_features'
URL_COLUMN_NAME = 'image_url'
FEATURES_COLUMN_NAME = 'features'


async def get_image_paths(directory):
    image_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.png')):
                full_path = os.path.join(root, file)
                image_paths.append(full_path)
    return image_paths


async def save_features_to_db(directory):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    image_paths = await get_image_paths(directory)

    pool = await aiomysql.create_pool(**DATABASE_CONFIG)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            with torch.no_grad():
                for path in image_paths:
                    image = preprocess(Image.open(path)).unsqueeze(0).to(device)
                    image_features = model.encode_image(image)
                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    features = image_features.cpu().numpy().flatten()

                    # Construct the image URL (modify this according to your actual URL structure)
                    image_url = f'http://yourserver.com/images/{os.path.basename(path)}'

                    # Insert URL and features into the database (modify this according to your actual schema)
                    await cursor.execute(
                        f"INSERT INTO {TABLE_NAME} ({URL_COLUMN_NAME}, {FEATURES_COLUMN_NAME}) VALUES (%s, %s)",
                        (image_url, features.tobytes())
                    )
            await conn.commit()
    pool.close()
    await pool.wait_closed()


if __name__ == "__main__":
    directory = 'path_to_your_image_directory'
    asyncio.get_event_loop().run_until_complete(save_features_to_db(directory))