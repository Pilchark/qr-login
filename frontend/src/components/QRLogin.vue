<template>
  <div class="qr-login">
    <div v-if="qrCodeUrl" class="qr-container">
      <!-- <img :src="qrCodeUrl" alt="QR Code" />  update if confirmed ,do not show the picture -->
      <img v-if="status !== 'CONFIRMED'" :src="qrCodeUrl" alt="QR Code" />
      <p>{{ statusMessage }}</p>
      <button v-if="status === 'EXPIRED'" @click="refreshQRCode">
        刷新二维码
      </button>
    </div>
    <div v-else class="loading">
      加载中...
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'QRLogin',
  data() {
    return {
      qrCodeUrl: '',
      qrCodeId: '',
      status: 'PENDING',
      statusMessage: '请使用手机扫描二维码登录',
      pollingInterval: null
    }
  },
  created() {
    this.generateQRCode();
  },
  beforeDestroy() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  },
  methods: {
    async generateQRCode() {
      try {
        const response = await axios.get('/api/login/qr/generate');
        this.qrCodeId = response.data.qr_code_id;
        this.qrCodeUrl = response.data.qr_image_url;
        this.startPolling();
      } catch (error) {
        console.error('生成二维码失败:', error);
        this.statusMessage = '生成二维码失败，请重试';
      }
    },
    startPolling() {
      this.pollingInterval = setInterval(async () => {
        try {
          const response = await axios.get(`/api/login/qr/check/${this.qrCodeId}`);
          this.status = response.data.status;
          
          switch (this.status) {
            case 'PENDING':
              this.statusMessage = '请使用手机扫描二维码登录';
              break;
            case 'SCANNED':
              this.statusMessage = '已扫描，请在手机上确认';
              break;
            case 'CONFIRMED':
              this.statusMessage = '登录成功，正在跳转...';
              clearInterval(this.pollingInterval);
              this.handleLoginSuccess();
              break;
            case 'EXPIRED':
              this.statusMessage = '二维码已过期，请点击刷新';
              clearInterval(this.pollingInterval);
              break;
          }
        } catch (error) {
          console.error('检查状态失败:', error);
        }
      }, 2000);
    },
    refreshQRCode() {
      this.generateQRCode();
    },
    handleLoginSuccess() {
      // 登录成功后的处理
      setTimeout(() => {
        this.$router.push('/home'); // 假设有一个 home 路由
      }, 1000);
    }
  }
}
</script>

<style scoped>
.qr-login {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.qr-container {
  text-align: center;
}

.qr-container img {
  max-width: 200px;
  margin-bottom: 15px;
}

button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.loading {
  margin: 20px;
}
</style>
