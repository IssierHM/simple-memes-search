import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios';
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as Icons from '@element-plus/icons-vue'
import './style/custom-style.scss';


// 创建Vue应用实例
const app = createApp(App);

// 使用Element Plus
app.use(ElementPlus);
//axios
app.config.globalProperties.$http = axios

for (let i in Icons) {
  app.component(i, Icons[i])
}

// 挂载Vue应用到 #app 元素上
app.use(router).mount('#app');
