<template>
  <div class="common-layout">
      <el-container class="input">
        <div class="header-container">
          <h2>meme图像检索</h2>
          <h3 class="header">请输入关键词并将目标图片上传</h3>
        </div>
        <el-form :model="formInline" class="demo-form-inline">
          <el-form-item label="关键词">
            <el-input v-model="formInline.text" placeholder="关键词" clearable />
          </el-form-item>
          <el-form-item>
            <el-upload
              class="upload-demo"
              ref="uploadRef"
              drag
              action="#"
              :before-upload="handleBeforeUpload"
              :on-change="handleChange"
              :file-list="fileList"
            >
              <div class="el-upload__text">
                请将文件拖入或 <em>点击以上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  请上传JPG/PNG格式
                </div>
              </template>
              <img v-if="formInline.image_base64" :src="formInline.image_base64" alt="Uploaded Image" />
              <img v-else src="../assets/image/show.jpg" alt="Default Image" />
            </el-upload>
          </el-form-item>
          <el-button type="primary" @click="uploadImages">请求数据</el-button>
        </el-form>
      <el-footer>
        <h3>结果展示</h3>
        <div class="demo-image__lazy">
          <el-image v-for="(url, index) in backInline" :key="index" :src="url" lazy />
          <!-- <img  src="../assets/image/show.jpg" alt="Default Image" />
          <img  src="../assets/image/2.jpg" alt="Default Image" />
          <img  src="../assets/image/2.jpg" alt="Default Image" />
          <img  src="../assets/image/2.jpg" alt="Default Image" /> -->
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const formInline = ref({
  text: '',
  image_base64: '' // 将image_base64定义为一个空字符串
})
const backInline = ref([]) 
const fileList = ref([]) // 用于管理上传文件列表

function handleBeforeUpload(file) {
  // 创建一个 FileReader 对象
  const reader = new FileReader();

  // 当读取完成时触发 onload 事件
  reader.onload = (event) => {
    // 将读取的结果（base64 编码的图片字符串）存储到 formInline.image_base64
    formInline.value.image_base64 = event.target.result;
  };

  // 读取文件并将其作为 Data URL（base64 编码）存储
  reader.readAsDataURL(file);

  // 阻止自动上传
  return false;
}

function handleChange(file, fileList) {
  // 限制只能上传一张图片
  if (fileList.length > 1) {
    fileList.splice(0, fileList.length - 1)
  }
}

const uploadImages = () => {
  // Create a new FormData instance
  const formData = new FormData();
  const text = formInline.value.text; // Retrieve the value of 'text' from the reactive reference

  // Append 'text' and 'image_base64' to the FormData object
  formData.append('text', text);
  formData.append('image_base64', formInline.value.image_base64);

  // Send the FormData to the server using a POST request
  axios.post('http://localhost:11451/search', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
  })
  .then((response) => {
    console.log('Upload successful:', response.data);
    // 假设后端返回的图片是 PNG 格式
    backInline.value = response.data.images.map(img => `data:image/png;base64,${img}`);
  })
  .catch((error) => {
    console.error('Error during upload:', error);
  });
}
</script>

<style scoped>
.demo-form-inline .el-input {
  width: 200px;
}
.demo-image__lazy {
  max-height: 400px; 
  display: fixed;
  flex: 1;
}


.demo-image__lazy img:last-child {
  margin-bottom: 0;
}

.demo-image__lazy  img {
  /* max-width: 50%;
  max-height: 50%;
  margin-bottom: 10px; */
  clip:rect(100%,100%);
   
}
.input {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  position: relative; /* 添加定位属性 */
}

.header-container .header {
  margin: 0;
  text-align: center;
  position: absolute; /* 使用绝对定位 */
  left: 50%; /* 将左侧位置设为父容器宽度的一半 */
  transform: translateX(-50%); /* 通过偏移来实现居中 */
}
</style>