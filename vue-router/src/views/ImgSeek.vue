<template>
  <div class="common-layout">
    <el-container>
      <el-header>###################################################################</el-header>
      <el-main class="input">
        <h3>请输入关键词并将需要识别的图片放入框中</h3>
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
            </el-upload>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="uploadImages">请求数据</el-button>
          </el-form-item>
        </el-form>
      </el-main>
      <el-main>
        <h3>结果展示</h3>
        <ul class="infinite-list" style="overflow: auto">
          <li v-for="(image, index) in backInline.image_base64" :key="index" class="infinite-list-item">
            <img :src="image" alt="Image">
          </li>
        </ul>
      </el-main>
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
const backInline = ref({
  image_base64: []
})
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
    backInline.value.image_base64 = response.data.images.map(img => `data:image/png;base64,${img}`);
  })
  .catch((error) => {
    console.error('Error during upload:', error);
  });
}
</script>


<style scoped>
.demo-form-inline .el-input {
  width: 220px;
}

.demo-form-inline .el-select {
  width: 220px;
}

.infinite-list {
  height: 100%;
  padding: 0;
  margin: 0;
  list-style: none;
}

.infinite-list .infinite-list-item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 50px;
  background: var(--el-color-primary-light-9);
  margin: 10px;
  color: var(--el-color-primary);
}

.infinite-list .infinite-list-item + .list-item {
  margin-top: 10px;
}

.input {
  height: 40px;
}

</style>