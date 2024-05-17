<template>
  <el-container class="common-layout">
    <el-header>
      <h1>meme检索演示</h1>
    </el-header>
    <el-container>
      <el-main>
        <el-menu
         router
          ellipsis
          class="el-menu-popper-demo"
          mode="horizontal"
          :popper-offset="16"
          style="max-width: 600px"
        >
          <el-menu-item index="/">
            <!-- <router-link to="/" class="button-full"> -->
              项目简介
            <!-- </router-link> -->
          </el-menu-item>
          <el-menu-item index="/search">
            <!-- <router-link to="/Img" class="button-full"> -->
              图像识别
            <!-- </router-link> -->
          </el-menu-item>
        </el-menu>
      </el-main>
      <el-footer>
        <router-view />
        <el-affix position="bottom" :offset="20" >
          <el-button type="primary" @click="scrollToTop">回到首页</el-button>
         </el-affix> 
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};
</script>

<style>
.common-layout {
  height: 200vh;
}
.el-container {
  height: 80%;
}
.el-header .el-main {
  height: 20%;
  position: fixed;
}
.el-footer {
  height: auto;
  margin-top: 5px;
  margin-bottom: 5px;
}
.button-full {
  width: 100%;
}
</style>
