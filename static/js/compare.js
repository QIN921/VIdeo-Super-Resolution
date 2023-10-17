// 选择待超分文件
const result = document.getElementById('result');
const form = document.getElementById('fileForm');

form.addEventListener('submit', function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('fileInput');
    
    if (fileInput.files.length === 0) {
        result.textContent = '请选择文件';
        return;
    }

    const formData = new FormData();

    formData.append('file', fileInput.files[0]);

    fetch('/upload_1', { // 修改为上传处理的URL
        method: 'POST',
        body: formData
    }).then(response => response.text())
      .then(data => {
          result.textContent = data;
      });
});

let leftFileIndex = 0;
let rightFileIndex = 0;
let leftImageFiles = [];
let rightImageFiles = [];

const leftFolderUploadInput = document.getElementById('leftFolderUpload');
const rightFolderUploadInput = document.getElementById('rightFolderUpload');
const leftPreviewDiv = document.getElementById('leftPreview');
const rightPreviewDiv = document.getElementById('rightPreview');
const previousBtn = document.getElementById('previousBtn');
const nextBtn = document.getElementById('nextBtn');
const zoomInBtn = document.getElementById('zoomInBtn');
const zoomOutBtn = document.getElementById('zoomOutBtn');
const zoomBtn = document.getElementById('zoomBtn');
let scaleFactor = 0.2;
var scrollLeft = 1220;
var scrollTop = 700;

leftFolderUploadInput.addEventListener('change', (event) => {
    const files = Array.from(event.target.files);
    leftImageFiles = files.filter(file => file.type.startsWith('image/'));
    leftImageFiles.sort((a, b) => getImageIndex(a) - getImageIndex(b));  // 按照图片索引进行排序
    leftFileIndex = 0;
    showImage('left');      
});

rightFolderUploadInput.addEventListener('change', (event) => {
    const files = Array.from(event.target.files);
    rightImageFiles = files.filter(file => file.type.startsWith('image/'));
    rightImageFiles.sort((a, b) => getImageIndex(a) - getImageIndex(b));  // 按照图片索引进行排序
    rightFileIndex = 0;
    showImage('right');
});

function getImageIndex(file) {
    const fileName = file.name.toLowerCase();
    const match = fileName.match(/frame_(\d+)\.(png|jpg)/);
    return match ? parseInt(match[1]) : -1;
}

function showImage(side) {
    let imageFiles, fileIndex, previewDiv;
    if (side === 'left') {
        imageFiles = leftImageFiles;
        fileIndex = leftFileIndex;
        previewDiv = leftPreviewDiv;
    } else {
        imageFiles = rightImageFiles;
        fileIndex = rightFileIndex;
        previewDiv = rightPreviewDiv;
    }

    if (imageFiles.length === 0) {
        previewDiv.innerHTML = '没有选择图片文件夹或文件夹内没有图片';
        return;
    }
    
    const file = imageFiles[fileIndex];
    const reader = new FileReader();
    reader.onload = function() {
        const image = new Image();
        image.src = reader.result;
        image.id = 'preview-image';
        image.style.transform = `scale(${scaleFactor})`;
        previewDiv.innerHTML = '';
        previewDiv.appendChild(image);
        if (image.naturalWidth != 0) {
            scrollTop = Math.floor(image.naturalHeight * 5 / 14);
            scrollLeft = Math.floor(image.naturalWidth * 5 / 14);
            console.log(scrollLeft);
        };
    };
    
    reader.readAsDataURL(file);
    previousBtn.disabled = (fileIndex === 0);
    nextBtn.disabled = (fileIndex === imageFiles.length - 1);
}

function showPrevious() {
    if (leftFileIndex > 0) {
        leftFileIndex--;
        showImage('left');
    }
    if (rightFileIndex > 0) {
        rightFileIndex--;
        showImage('right');
    }
}

function showNext() {
    if (leftFileIndex < leftImageFiles.length - 1) {
        leftFileIndex++;
        showImage('left');
    }
    if (rightFileIndex < rightImageFiles.length - 1) {
        rightFileIndex++;
        showImage('right');
    }
}

function zoomIn() {
    scaleFactor += 0.1;
    applyTransform('left');
    applyTransform('right'); // 调用applyTransform函数对右边图片进行缩放
}

function zoomOut() {
    scaleFactor -= 0.1;
    applyTransform('left');
    applyTransform('right'); // 调用applyTransform函数对右边图片进行缩放
}

function resetZoom() {
    scaleFactor = 0.2;
    
    applyTransform('left');
    leftPreviewDiv.scrollTop = 747;
    leftPreviewDiv.scrollLeft = 1328;

    applyTransform('right');
    rightPreviewDiv.scrollTop = 747;
    rightPreviewDiv.scrollLeft = 1328; 
}

function applyTransform(side) {
    const image = document.querySelector(`#${side}Preview #preview-image`);
    if (image != null) {  // 如果该侧存在图片，则进行缩放操作
        image.style.transform = `scale(${scaleFactor})`;
    }
}

function syncScroll(side) {
    const leftScrollTop = leftPreviewDiv.scrollTop;
    const leftScrollLeft = leftPreviewDiv.scrollLeft;
    const rightPreviewDiv = document.getElementById('rightPreview');
    
    if (side === 'left') {
        rightPreviewDiv.scrollTop = leftScrollTop;
        rightPreviewDiv.scrollLeft = leftScrollLeft;
    } else {
        leftPreviewDiv.scrollTop = rightPreviewDiv.scrollTop;
        leftPreviewDiv.scrollLeft = rightPreviewDiv.scrollLeft;
    }
}

// 消息显示
var socket = io();
//记录上一次显示位置
var lastloc = null;
socket.on("connect", function () {

});

socket.on("server_response", function (msg) {
    //接收到后端发送过来的消息
    var t = msg.data;
    console.log('message: ' + t);
    $('#messagecontainer').append(t +'<br/>');
});

socket.on("server_response_num", function (msg) {
    //接收到后端发送过来的消息
    var t = msg.data;
    console.log('process: ' + t);
    var progressBar = document.getElementById("progress");

    // 计算进度百分比
    var progressPercent = t * 100;
    // 更新进度条宽度
    progressBar.style.width = progressPercent + "%";
});
