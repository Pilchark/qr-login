# dev history

1. dev backend server(vue)
2. dev frontend server
3. docker start redis server
4. save qr-code image to redis

前端主要功能：
1. 自动生成并显示二维码
2. 定期轮询检查二维码状态
3. 根据不同状态显示不同提示信息
4. 支持二维码过期后刷新
5. 登录成功后可以跳转到其他页面

使用说明：
1. 确保后端服务器正在运行
2. 启动前端开发服务器 `npm run serve`
3. 在浏览器中访问 http://127.0.0.1:8000

注意事项：
1. 实际生产环境中应该使用更安全的通信方式
2. 需要添加适当的错误处理
3. 可以根据需要调整轮询间隔时间
4. 可以添加加载动画和更多的交互效果
5. 建议使用 WebSocket 替代轮询机制以提高效率
