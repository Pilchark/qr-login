<template>
  <div id="app">
    <h1>扫码登录示例</h1>
    <QRLogin />
  </div>
</template>

<script>
import QRLogin from './components/QRLogin.vue'

export default {
  name: 'App',
  components: {
    QRLogin
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
