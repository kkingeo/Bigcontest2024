const express = require('express');
const path = require('path');
const app = express();

// 정적 파일 제공 (CSS, JS, 이미지 등)
app.use(express.static('webpage'));

// HTML 파일 제공
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'webpage', 'index.html'));
});

// 서버 실행
app.listen(3000, () => {
    console.log('Server is running on http://127.0.0.1:3000');
});
