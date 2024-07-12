<template>
  <div id="app">
    <!-- <router-view ></router-view> -->
    <router-view v-if="!toReload"></router-view>
  </div>
  <!-- <el-affix position="bottom" :offset="20" >
    <el-button type="primary" @click="scrollToTop">回到首页</el-button>
  </el-affix>  -->
</template>

<script setup>
// const scrollToTop = () => {
//   window.scrollTo({ top: 0, behavior: 'smooth' });
// };
</script>

<style>
body{
  margin: 0px;
  background-image: url("./assets/image/background.jpg");
  background-repeat:no-repeat;
  background-attachment:fixed;
  background-size: cover;
}
.common-layout {
  min-height: 100vh;
}
.main {
  height: auto;
  align-items: center;
}
.el-header {
  background-color: #ffffffe5;
  position: fixed;
  display: flex;
  justify-content: space-between;
  height: 50px;
  width: 100%;
  top: 0;
  z-index: 1000;
}
.el-main {
  margin-top: 100px;
  position:absolute;
  background-color: #ffffffe5;
  height: auto;
  width: 80%;
  box-shadow: 0 0 15px 10px rgba(0, 0, 0, .3);
  border-radius: 15px;
  display: flex;
  justify-content: space-between; 
  align-items: start;
  flex-direction: row;
  }
.button-full {
  width: 100%;
}
</style>
