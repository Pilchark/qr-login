import os
import qrcode
import uuid
import redis
import time
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# 使用Redis存储二维码状态
redis_client = redis.Redis(host='localhost', port=6379, db=0)

SERVER_IP = "http://127.0.0.1:5000"

class QRCodeLogin:
    def __init__(self):
        self.expire_time = 180  # 二维码有效期180秒
        
    def generate_qrcode(self):
        """生成二维码及相关信息"""
        # 生成唯一的二维码ID
        print("Generating QR code...")
        qr_code_id = str(uuid.uuid4())
        
        # 生成二维码内容（包含服务器地址和二维码ID）
        qr_content = f"{SERVER_IP}/verify/{qr_code_id}"
        
        # 生成二维码图片
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_content)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # 保存二维码状态到Redis
        redis_client.set(f"qr:{qr_code_id}", "PENDING")
        redis_client.expire(f"qr:{qr_code_id}", self.expire_time)

        # save qr image to file
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        saved_dir = os.path.join(cur_dir, "qr_images")
        if not os.path.exists(saved_dir):
            os.makedirs(saved_dir)
        qr_img.save(os.path.join(saved_dir, f"{qr_code_id}.png"))
        
        return {
            "qr_code_id": qr_code_id,
            "qr_image": qr_img,
            "expire_time": self.expire_time
        }

    def check_scan_status(self, qr_code_id):
        """检查二维码扫描状态"""
        status = redis_client.get(f"qr:{qr_code_id}")
        if status:
            return status.decode()
        return "EXPIRED"

@app.route('/api/login/qr/generate')
def generate_login_qr():
    """生成登录二维码"""
    qr_login = QRCodeLogin()
    result = qr_login.generate_qrcode()

    # 返回二维码信息
    return jsonify({
        "qr_code_id": result["qr_code_id"],
        # "qr_image_url": f"/qr_images/{result['qr_code_id']}.png" # return SERVER_IP + qr_image_url
        "qr_image_url": f"{SERVER_IP}/api/qr_images/{result['qr_code_id']}.png"
    })

@app.route('/api/login/qr/check/<qr_code_id>')
def check_qr_status(qr_code_id):
    """检查二维码状态"""
    qr_login = QRCodeLogin()
    status = qr_login.check_scan_status(qr_code_id)
    return jsonify({"status": status})

@app.route('/api/login/qr/confirm/<qr_code_id>', methods=['POST'])
def confirm_login(qr_code_id):
    #TODO verify user login
    # set qr code status to CONFIRMED
    redis_client.set(f"qr:{qr_code_id}", "CONFIRMED")
    return jsonify({"message": "Login confirmed"})

# qr code url
@app.route('/api/qr_images/<qr_code_id>.png')
def get_qr_image(qr_code_id):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    saved_dir = os.path.join(cur_dir, "qr_images")
    return send_from_directory(saved_dir, f"{qr_code_id}.png")

# use jinja2 render a html page for /verify/<qr_code_id>
@app.route('/verify/<qr_code_id>')
def verify(qr_code_id):
    # set qr code status to SCANNED
    redis_client.set(f"qr:{qr_code_id}", "SCANNED")
    return f"""
    <html>
        <head>
            <title>QR Code Verification</title>
            <script>
                function checkStatus() {{
                    fetch('/api/login/qr/check/{qr_code_id}')
                        .then(response => response.json())
                        .then(data => {{
                            if (data.status === 'CONFIRMED') {{
                                window.location.href = '/api/login/qr/confirm/{qr_code_id}';
                            }}
                        }});
                }}
                setInterval(checkStatus, 1000);
            </script>
        </head>
        <body>
            <h1>QR Code Verification</h1>
            // show qr code id
            <p>QR Code ID: {qr_code_id}</p>
            // create a button to confirm login, if click, use post method to confirm login
            <button onclick="fetch('/api/login/qr/confirm/{qr_code_id}', {{ method: 'POST' }})">Confirm Login</button>
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run(port=5000)
