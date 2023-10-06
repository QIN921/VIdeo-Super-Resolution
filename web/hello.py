import shutil
from flask import Flask, request
from flask_socketio import SocketIO
import os
from threading import Lock

app = Flask(
    __name__,
    template_folder='.',  # 模板文件
    static_folder='.',  # 虚拟资源入口
    static_url_path='',
)
thread = None
thread_lock = Lock()
socketio = SocketIO(app, cors_allowed_origins='*')
connected_sids = set()


def clear_folder(folder_path):
    # 检查目标文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹 '{folder_path}' 不存在。")
        return

    # 遍历并删除文件夹中的所有文件和子文件夹
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"清除文件 '{file_path}' 时出现错误：{e}")


@app.route('/upload_2', methods=['POST'])
def efficient():
    if 'file' not in request.files:
        return "没有选择文件"

    file = request.files['file']
    filename = file.filename

    selected_scale = request.form['scale']  # 获取放大倍数
    if not selected_scale:
        print('无放大倍数')
        selected_scale = 2

    # 保存文件到指定目录
    save_path = './video'
    file_abs_path = os.path.join(save_path, filename)
    file.save(file_abs_path)

    # 以文件绝对地址代替上传文件内容
    file_input = file_abs_path
    clear_folder("./video/frame")
    clear_folder("./video/output")
    os.system(f"ffmpeg -i {file_input} ./video/frame/%05d.jpg -y")
    print("视频抽帧完成！")
    socketio.emit("server_response_2", {'data': "视频抽帧完成"})
    os.system(
        f'../realcugan/realcugan-ncnn-vulkan.exe -i ./video/frame -s {selected_scale} -o ./video/output')
    socketio.emit("server_response_2", {'data': "视频超分完成"})
    os.system(f"ffmpeg -i ./video/output/%05d.png -pix_fmt yuv420p -c:v libx264 ./video/output.mp4 -y")
    socketio.emit('server_response_2', {'data': f"Realcugan超分{selected_scale}倍结果保存至./video/output.mp4"})
    return f"已对 {filename} 进行超分，并保存到 output.mp4"


@app.route("/upload_1", methods=['POST'])
def quality():
    if 'file' not in request.files:
        return "没有选择文件"

    file = request.files['file']
    filename = file.filename
    # 保存文件到指定目录
    save_path = './video'
    file_abs_path = os.path.join(save_path, filename)
    file.save(file_abs_path)
    file_input = file_abs_path
    clear_folder("./video/frame")
    clear_folder("./video/direct")
    clear_folder("./video/output")
    # 视频抽帧
    os.system(f"ffmpeg -i {file_input} ./video/frame/%05d.jpg -y")
    print("视频抽帧完成！")
    socketio.emit('server_response', {'data': "视频抽帧完成"})
    # 输入文件夹进行超分
    os.system("python ../inference_realbasicvsr.py ../configs/realbasicvsr_x4.py ../checkpoints/RealBasicVSR_x4.pth "
              "./video/frame ./video/output --max_seq_len 8")
    socketio.emit('server_response', {'data': "视频超分完成！"})
    #  直接放大，方便对比效果
    os.system("ffmpeg -i ./video/frame/%05d.jpg -vf scale=iw*4:ih*4 ./video/direct/%05d.jpg -y")
    socketio.emit('server_response', {'data': "视频抽帧结果保存至./video/frame"})
    socketio.emit('server_response', {'data': "RealBasicVSR_x4超分结果保存至./video/output"})
    socketio.emit('server_response', {'data': "FFmpeg直接放大结果保存至./video/direct"})
    return f"已对 {filename} 进行超分，并保存到 ./video/output"


@app.route("/")
def index():
    with open('index.html', encoding='utf8') as f:
        return "".join(f.readlines())


# 后端程序
# def background_thread():
#     """
#     该线程专门用来给前端发送消息
#     :return:
#     """
#     num = 0
#     while True:
#         socketio.emit('server_response', {'data': num % 16 + 1})
#         socketio.sleep(2)
#         num += 1


@socketio.on('connect')
def on_connect():
    connected_sids.add(request.sid)
    print(f'{request.sid} 已连接')
    # global thread
    # with thread_lock:
    #     print(thread)
    #     if thread is None:
    #         # 如果socket连接，则开启一个线程，专门给前端发送消息
    #         thread = socketio.start_background_task(target=background_thread)


@socketio.on('disconnect')
def on_disconnect():
    connected_sids.remove(request.sid)
    print(f'{request.sid} 已断开')


@socketio.on('message')
def handle_message(message):
    """收消息"""
    data = message['data']
    print(f'{request.sid} {data}')


if __name__ == '__main__':
    # app.run()
    socketio.run(app, host='127.0.0.1', port=8083, allow_unsafe_werkzeug=True, debug=True)
