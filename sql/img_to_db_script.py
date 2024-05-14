import aiomysql
import asyncio
import clip
import torch
from PIL import Image
import os
import numpy as np

# Replace with your actual database configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': '96196',
    'db': 'Test',
    'charset': 'utf8mb4',
    'autocommit': True
}

# Replace with your actual table name and column names
TABLE_NAME = 'image'
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
                    # Use the local file path instead of a URL
                    local_image_path = path

                    # Check if the image path already exists in the database
                    await cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE {URL_COLUMN_NAME} = %s", (local_image_path,))
                    (count,) = await cursor.fetchone()
                    if count > 0:
                        # Skip this image because its path already exists in the database
                        continue

                    image = preprocess(Image.open(path)).unsqueeze(0).to(device)
                    image_features = model.encode_image(image)
                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    features = image_features.cpu().numpy()
                    features = features.astype(np.float32)
                    features_bytes = features.tobytes()

                    # 存储特征时，还需要存储形状信息
                    shape_bytes = np.array(features.shape).tobytes()

                    # 将路径、特征和形状插入数据库
                    await cursor.execute(
                        f"INSERT INTO {TABLE_NAME} ({URL_COLUMN_NAME}, {FEATURES_COLUMN_NAME}, shape) VALUES (%s, %s, %s)",
                        (local_image_path, features_bytes, shape_bytes)
                    )
            await conn.commit()
    pool.close()
    await pool.wait_closed()


if __name__ == "__main__":
    directory = '../imgs/'
    asyncio.get_event_loop().run_until_complete(save_features_to_db(directory))