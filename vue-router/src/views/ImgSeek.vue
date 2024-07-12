<template>
  <div class="common-layout">
    <el-container class="main">
      <el-header>
        <div class="left-content">
          <a href="/" target="_self">
            <img src="../assets/logo.png" alt="Logo" style="height: 60px;"> <!-- 替换为您的 logo 路径 -->
          </a>
        </div>
        <div class="right-content">
          <a href="https://github.com/IssierHM/simple-memes-search" target="_blank">
            <img src="../assets/image/github-mark.png" alt="GitHub" style="height: 40px;"> 
          </a>
        </div>
      </el-header>
      <el-main>
        <div class="search">
          <el-container class="input">
            <el-form :model="formInline" class="demo-form-inline">
              <el-form-item label="输入文本">
                <el-input v-model="formInline.text" placeholder="请输入文本" clearable />
              </el-form-item>
              <el-form-item>
                <el-upload
                  v-model:file-list="fileList"
                  class="upload-demo"
                  ref="uploadRef"
                  drag
                  action="#"
                  :before-upload="handleBeforeUpload"
                  :on-change="handleChange"
                  list-type="picture"
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    请将文件拖入或 <em>点击以上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      请上传JPG/PNG格式
                    </div>
                  </template>
                  <div class="preview-image">
                    <!-- <span class="demonstration">{{ fit }}</span> -->
                    <el-image v-if="formInline.image_base64" style="width: 300px; height: 300px" :src="formInline.image_base64" :fit="fit" />
                    <el-image v-else style="width: 250px; height: 250px" :src="slotImage" :fit="fit_contain"/>
    
                  </div>
                  <!-- <img v-if="formInline.image_base64" :src="formInline.image_base64" alt="Uploaded Image" /> -->
                  <!-- <img v-else src="../assets/image/show.jpg" alt="Default Image" /> -->
                </el-upload>
              </el-form-item>
              <el-form-item label="返回数量">
                <el-slider v-model="sliderValue" :min="1" :max="20" :step="1" />
              </el-form-item>
              <el-button type="primary" @click="uploadImages">检索</el-button>
            </el-form>
          </el-container>
          <el-container class="result-output">
            <!-- <div class="demo-image__lazy"> -->
            <!-- <el-space warp> -->
            <div v-for="(item, index) in backInline" :key="index" class="demo-image__preview">
              <el-image  
              style="width: 300px; height: 300px"
              :src="item" :fit="fit" lazy />
              <div class="mask">
                <div class="zoomInImg svgBox" @click="showImgView(item, index)">
                  <el-icon size="30">
                    <ZoomIn />
                  </el-icon>
                </div>
              </div>
              <el-image-viewer @close="() => { showViewer = false }" v-if="showViewer" :url-list="urlList" />
            </div>
            
            <!-- </el-space> -->
                <!-- <img  src="../assets/image/show.jpg" alt="Default Image" />
                <img  src="../assets/image/2.jpg" alt="Default Image" />
                <img  src="../assets/image/2.jpg" alt="Default Image" />
                <img  src="../assets/image/2.jpg" alt="Default Image" /> -->
            <!-- </div> -->
          </el-container>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { UploadFilled } from '@element-plus/icons-vue'

const fit = 'cover'
const fit_contain = 'contain'
const slotImage = require("../assets/image/show.gif")
const formInline = ref({
  text: '',
  image_base64: '' // 将image_base64定义为一个空字符串
})
const backInline = ref([]) 
const fileList = ref([]) // 用于管理上传文件列表
const sliderValue = ref(4)

const showViewer = ref(false)
const urlList = ref([])

const showImgView = (item, index) => {
  console.log(index)
  showViewer.value = true
  urlList.value = [item]
}

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
  formData.append('image_count', sliderValue.value);

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
.left-content {
  display: flex;
  align-items: center;
}
.right-content {
  display: flex;
  align-items: center;
}
.demo-form-inline .el-input {
  width: 300px;
}
.demo-image__lazy {
  display: flex;
}

.demo-image__lazy img:last-child {
  margin-bottom: 0;
}
.search {
  display: flex;
  justify-content: space-between; 
  align-items: start;
  flex-direction: row;
}
.input {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width:40%;
}
.result-output{
  display: flex;
  border-radius: 15px;
  background-color: rgba(231, 231, 231, 0.973);
  height: 80vh;
  width: 60%;
  display: flex;
  flex-wrap: wrap; /* 子元素在必要时换行 */
  justify-content: space-between; /* 控制行内项目的对齐方式 */
  align-items: flex-start; /* 控制交叉轴上的对齐方式 */
  overflow-y: auto;
}
.result-output >div {
  width: 300px;
  height:300px;
  margin: 10px;
  border: 2px solid;
  position: relative;
  border-image: linear-gradient(#67518b, #397f88) 30;
  &:hover {
    .mask {
      opacity: 1;
    }
    img {
      transform: scale(1.1);
    }
  }
  .mask {
    transition: all 0.5s;
    opacity: 0;
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background: rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
 
    .svgBox {
      height: 50px;
      width: 50px;
      background: rgb(0, 0, 0, 0.3);
      border-radius: 50%;
      margin: 10px;
      padding: 10px;
      cursor: pointer;
      display: flex;
      align-items: center; 
      justify-content: center;
    }
 
    .zoomInImg {
      color: #fff;
    }
  }
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

.upload-demo {
  width: 400px; /* 设置宽度 */

}
</style>