<template>
  <div id="app">
    <el-container style="height: 100vh;">
      <!-- 侧边栏 -->
      <el-aside width="200px" style="background-color: #f0f2f5;">
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical-demo"
          @select="handleMenuSelect"
        >
          <el-menu-item index="test-edge">
            <el-icon><Monitor /></el-icon>
            <span>测试Edge页面</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <el-header style="background-color: #fff; border-bottom: 1px solid #e4e7ed;">
          <h1>Edge页面自动化测试工具</h1>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor } from '@element-plus/icons-vue'

const router = useRouter()
const activeMenu = ref('test-edge')

const handleMenuSelect = (key) => {
  activeMenu.value = key
  router.push(`/${key}`)
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

h1 {
  font-size: 20px;
  line-height: 60px;
  margin: 0;
}

.el-menu-vertical-demo {
  height: 100%;
}
</style>
