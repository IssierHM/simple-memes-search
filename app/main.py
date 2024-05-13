from fastapi import FastAPI, Form, HTTPException
import uvicorn
import aiomysql
import base64
from typing import List, Tuple
from io import BytesIO
from PIL import Image
import os
from model.clip import load, tokenize
import numpy as np
from typing import Optional
import torch

app = FastAPI()

# 加载CLIP模型
model, preprocess = load("ViT-B/32", device="cpu")


async def create_db_pool():
    # 创建数据库连接池
    return await aiomysql.create_pool(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        port=int(os.getenv('DB_PORT', 114514)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '1919810'),
        db=os.getenv('DB_NAME', 'Test'),
        charset='utf8mb4',
        autocommit=True,
    )


@app.on_event("startup")
async def startup_event():
    app.state.db_pool = await create_db_pool()


@app.on_event("shutdown")
async def shutdown_event():
    app.state.db_pool.close()
    await app.state.db_pool.wait_closed()


async def get_similar_images(pool, input_feature: torch.Tensor) -> List[str]:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT image_url, features FROM image_features")
            results = await cursor.fetchall()

            # 计算每个图片特征与输入特征的相似度
            similarities = []
            for row in results:
                db_feature = torch.from_numpy(np.frombuffer(row['features'], dtype=np.float32))
                similarity = torch.dot(db_feature, input_feature) / (torch.norm(db_feature) * torch.norm(input_feature))
                similarities.append((row['image_url'], similarity.item()))

            similarities.sort(key=lambda x: x[1], reverse=True)
            top_10_similar = similarities[:10]

    # 返回相似度最高的10个图片URL
    return [url for url, _ in top_10_similar]


async def base64_to_image(base64_str):
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data)).convert("RGB")
    return image


async def image_to_base64(image_path):
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')


def get_image_features(image):
    image_preprocessed = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        image_features = model.encode_image(image_preprocessed)
        image_features /= image_features.norm(dim=-1, keepdim=True)
    return image_features.cpu().numpy()


def get_text_features(text):
    text_tokens = tokenize([text])
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)
    return text_features.cpu().numpy()


@app.post("/search/")
async def search(image_base64: Optional[str] = Form(None), text: Optional[str] = Form(None)):
    img_results = []

    if image_base64 and text:
        img = base64_to_image(image_base64)
        input_img_feature = get_image_features(img)
        text_feature = get_text_features(text)
        input_feature = (text_feature + input_img_feature) / 2
        urls = await get_similar_images(app.state.db_pool, input_feature)
        img_results = [image_to_base64(url) for url in urls]

    elif image_base64:
        img = base64_to_image(image_base64)
        input_img_feature = get_image_features(img)
        urls = await get_similar_images(app.state.db_pool, input_img_feature)
        img_results = [image_to_base64(url) for url in urls]
    elif text:
        text_feature = get_text_features(text)
        urls = await get_similar_images(app.state.db_pool, text_feature)
        img_results = [image_to_base64(url) for url in urls]
    else:
        raise HTTPException(status_code=400, detail="No search input provided")

    return {
        "message": "Search completed successfully",
        "results": img_results
    }


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=11451)