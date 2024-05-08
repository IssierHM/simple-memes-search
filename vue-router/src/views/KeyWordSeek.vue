<template>
  <div>
    <el-container style="height: 100vh;">
      <el-container>
        <el-header><h2>###################################################################</h2></el-header>
        <el-main>
          <div class="demo-collapse">
            <!-- 想删除直接把对应盒子删了就行 -->
            <!-- 想添加直接加盒子
            或者css方法 -->
    <el-collapse accordion class="font_div">
      <el-collapse-item name="1">
        <template #title>
          项目介绍<el-icon class="header-icon">
            <info-filled />
          </el-icon>
        </template>
        <div>
          项目名称：基于哈基米的哈利路亚大旋风
        </div>
        <div>
          参考自：https://github.com/osmarks/meme-search-engine
        </div>
      </el-collapse-item>
      <el-collapse-item title="成员分工" name="2" > 
        <div>
          王一博：阿巴巴巴
        </div>
        <div>
          张志远：前端展示实现
        </div>
        <div>
          马俊：模型实现与数据训练
        </div>
        <div>
          朱佳裕：报告与发表
        </div>
        <div>
          范铸贤：后期优化
        </div>
        <div>
          陈子扬：无
        </div>
      </el-collapse-item>
      <el-collapse-item title="项目结果" name="3">
        <div>
          11111111111111111111111111111111111111
        </div>
        <div>
          2222222222222222222222222222
        </div>
      </el-collapse-item>
      <el-collapse-item title="我们的收获" name="4">
        <div>
          啊巴巴
        </div>
        <div>
          啊巴巴
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { InfoFilled } from '@element-plus/icons-vue'
</script>

<style>
.font_div{
  font-weight:bold;
}
</style>
