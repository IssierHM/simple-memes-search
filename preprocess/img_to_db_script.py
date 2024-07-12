import aiomysql
import asyncio
import cn_clip.clip as clip
from cn_clip.clip import load_from_name
import torch
from PIL import Image
import os
import numpy as np

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': '96196',
    'db': 'Test',
    'charset': 'utf8mb4',
    'autocommit': True
}

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
    # model, preprocess = load_from_name("ViT-L-14", device=device, download_root='../cn_clip/clip/')
    model, preprocess = load_from_name(
        "D:/project/memes-search/cn_clip/clip/pt/epoch_latest.pt",
        device=device,
        vision_model_name="ViT-L-14-336",
        text_model_name="RoBERTa-wwm-ext-base-chinese",
        input_resolution=336)

    image_paths = await get_image_paths(directory)

    pool = await aiomysql.create_pool(**DATABASE_CONFIG)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            with torch.no_grad():
                for path in image_paths:
                    local_image_path = path
                    await cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE {URL_COLUMN_NAME} = %s", (local_image_path,))
                    (count,) = await cursor.fetchone()
                    if count > 0:
                        continue

                    image = preprocess(Image.open(path)).unsqueeze(0).to(device)
                    image_features = model.encode_image(image)
                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    features = image_features.cpu().numpy()
                    features = features.astype(np.float32)

                    print(features.size)

                    features_bytes = features.tobytes()

                    shape_bytes = np.array(features.shape).tobytes()

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