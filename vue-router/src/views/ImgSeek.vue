<template>
  <div class="common-layout">
    <el-container>
      <el-header>###################################################################</el-header>
      <el-main class="input">
        <h3>请输入关键词并将需要识别的图片放入框中</h3>
        <el-form :model="formInline" class="demo-form-inline">
          <el-form-item label="关键词">
            <el-input v-model="formInline.KeyWords" placeholder="关键词" clearable />
          </el-form-item>
          <el-form-item>
            <!-- 自己的api！！！！！！！！！！！！！！！ -->
            <el-upload
              class="upload-demo"
              ref="uploadRef"
              drag
              action="#"
              :before-upload="handleBeforeUpload"
              multiple
            >
              <div class="el-upload__text">
                请将文件拖入或 <em>点击以上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  请上传JPG/PNG格式
                </div>
              </template>
            </el-upload>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="onSubmit">Query</el-button>
          </el-form-item>
        </el-form>
      </el-main>
      <el-main>
        <h3>结果展示</h3>
        <ul v-infinite-scroll="load" class="infinite-list" style="overflow: auto">
          <li v-for="i in count" :key="i" class="infinite-list-item">{{ i }}</li>
        </ul>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const count = ref(0)
const images = ref([])
// 返回的图片加载位置图片形式
const load = () => {
  axios.get('http://localhost:8080/' + count.value)
    .then(response => {
      images.value = images.value.concat(response.data.images)
      count.value++
    })
    .catch(error => {
      console.error('Error loading images:', error);
    });
}

const formInline = reactive({
  KeyWords: '',
})

const uploadRef = ref(null);
//根据后端要求转为base64格式
const handleBeforeUpload = (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      file.base64 = event.target.result;
      console.log('File converted to Base64:', file.base64); 
      resolve(file);
    };
    reader.readAsDataURL(file);
  });
};

const onSubmit = () => {
  const keywords = formInline.KeyWords;
  const uploadComponent = uploadRef.value;
  const fileList = uploadComponent.uploadFiles;
  const formData = new FormData();

  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i].base64;     
    formData.append('files[]', file); // 通过append向form对象添加数据
  }

  formData.append('keywords', keywords);
  // 表单上传位置
  axios.post('http://localhost:8081/', formData)
    .then(response => {
      console.log('Upload successful:', response.data);
    })
    .catch(error => {
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
