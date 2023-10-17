var src ='/video' //放置你要直播的地址
const dp = new DPlayer({
    container: document.getElementById('dplayer'),
    live: true,
    video: {
        url: `${src}`,
        type: 'hls',
    },
});

const form = document.getElementById('fileForm');
form.addEventListener('submit', function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('fileInput');
    
    if (fileInput.files.length === 0) {
        result.textContent = '请选择文件';
        return;
    }

    const formData = new FormData();
    const scaleSelect = document.getElementById('scaleSelect');
    const selectedScale = scaleSelect.value;

    formData.append('file', fileInput.files[0]);
    formData.append('scale', selectedScale)

    fetch('/upload_2', { // 修改为上传处理的URL
        method: 'POST',
        body: formData
    }).then(response => response.text())
        .then(data => {
            result.textContent = data;
        });
});   

var socket = io();
//记录上一次显示位置
var lastloc = null;
socket.on("connect", function () {

});

socket.on("server_response_2", function (msg) {
    //接收到后端发送过来的消息
    var t = msg.data;
    console.log('message: ' + t);
    $('#messagecontainer').append(t +'<br/>');
});

socket.on("video_size_2", function (msg) {
    //接收到后端发送过来的消息
    var t = msg.data;
    console.log('size: ' + t);
    $('#videosize').append(t +'<br/>');
});

function clearContent() {
    document.getElementById('videosize').innerHTML = "";
}