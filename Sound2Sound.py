from flask import Flask, render_template
from flask_socketio import SocketIO,join_room,leave_room
from threading import Lock
from sound import Recorder
import os
import random

async_mode = None

app = Flask(__name__)
app.debug = False
app.threaded = True
app.config['SECRET_KEY'] = os.urandom(32)


thread = None
thread_lock = Lock()
max_len = 40  # 目前为止效果最佳的参数

socket_io = SocketIO(app, async_mode=async_mode)


def bg_thread():
    recorder = Recorder()
    buffers = []

    def send(data):
        if len(buffers) < max_len:
            buffers.append(data)
        else:
            all_data = b''.join(buffers)  # + random.choice([b'1', b'12', b'123', b'1234', b'1235']) * 100

            # 广播给全部连接
            socket_io.emit('data', {'data': recorder.packer.pack(all_data)},
                           namespace='/sound', room='all')

            buffers.clear()

    recorder.start(send)


@app.route('/')
def index():
    return render_template('index.html', async_mode=socket_io.async_mode)


@socket_io.on('connect', namespace='/sound')
def connect():
    global thread
    with thread_lock:
        join_room('all',namespace='/sound')
        if thread is None:
            thread = socket_io.start_background_task(target=bg_thread)


@socket_io.on('disconnect', namespace='/sound')
def disconnect():
    with thread_lock:
        leave_room('all', namespace='/sound')


if __name__ == '__main__':
    from sys import argv
    try:
        host = argv[1]
        port = int(argv[2])
    except Exception as e:
        print('Usage %s ip port' % argv[0])
        host = '0.0.0.0'
        port = 9600

    socket_io.run(app, host=host, port=port)




