#!/usr/bin/env node

/*!
 * Node.js CGI Explorer : Neo (http://neo.s21.xrea.com/)
 * 
 * - 1行目の Shebang を node (node.exe) の実行パスに編集してください (#!/usr/bin/node など)
 * - 本ファイルに実行権限を付与してください
 * - 「定数」セクションでパスワードとルートディレクトリを設定してください
 */


// Require・例外ハンドリング定義
// ====================================================================================================

const fs   = require('fs');
const path = require('path');

process.on('uncaughtException', (error) => {
  console.log('Content-Type: text/html; charset=UTF-8\n\n');
  console.log('<pre style="color: #00f; font-weight: bold;">Uncaught Exception :<br>', error, '</pre>');
});


// 定数
// ====================================================================================================

/** パスワード : input[type="password"] に入力できる文字列であること */
const credential = 'CHANGE-THIS';
/** ルートディレクトリ : フルパスで指定・path.resolve() を使い末尾のスラッシュを除去しておく */
const rootDirectory = path.resolve('/PATH/TO/PRIVATE-DIRECTORY');


// 共通関数
// ====================================================================================================

/** HTML ヘッダ */
function writeHtmlHeader(title) {
  title = title || 'Index Of';
  
  console.log(`Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${title}</title>
    <style>

@font-face { font-family: "Yu Gothic"; src: local("Yu Gothic Medium"), local("YuGothic-Medium"); }
@font-face { font-family: "Yu Gothic"; src: local("Yu Gothic Bold")  , local("YuGothic-Bold")  ; font-weight: bold; }
*, ::before, ::after { box-sizing: border-box; }

html {
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, YuGothic, "Yu Gothic", "Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  overflow-y: scroll;
  cursor: default;
  text-decoration-skip-ink: none;
  -webkit-text-size-adjust: 100%;
  -webkit-text-decoration-skip: objects;
  -webkit-overflow-scrolling: touch;
}

body {
  margin: 1rem;
  line-height: 1.6;
  overflow-wrap: break-word;
}

a      { color: #00f; }
strong { color: #f00; }

button, [type="button"], [type="reset"], [type="submit"], [type="text"], [type="password"] {
  margin: 0;
  border: 1px solid #999;
  border-radius: 2px;
  padding: .25em .5em;
  color: inherit;
  font-family: inherit;
  font-size: inherit;
}

button, [type="button"], [type="reset"], [type="submit"] {
  padding-right: 1em;
  padding-left : 1em;
  background: #eee;
}

    </style>
  </head>
  <body>`);
}

/** HTML フッタ */
function writeHtmlFooter() {
  console.log('  </body>\n</html>');
}

/** エラーメッセージのみのページを出力する */
function showErrorPage(errorMessage) {
  writeHtmlHeader(errorMessage);
  console.log(`<p><strong>${errorMessage}</strong></p>`);
  writeHtmlFooter();
}


// ログインページ
// ====================================================================================================

/** ログインページ */
function showLoginPage(errorMessage) {
  writeHtmlHeader('Login');
  
  console.log(`
    <form action="${process.env.SCRIPT_NAME}" method="POST" id="form">
      <p><input type="password" name="credential" value="" id="credential"> <button type="button" id="button-submit">Login</button></p>
      <input type="hidden" name="mode" value="login">
    </form>
  `);
  
  if(errorMessage) {
    console.log(`<p><strong>${errorMessage}</strong></p>`);
  }
  
  console.log(`
    <script>
      document.addEventListener('DOMContentLoaded', () => {
        document.getElementById('button-submit').addEventListener('click', (event) => {
          localStorage.setItem('credential', document.getElementById('credential').value);
          document.getElementById('form').submit();
        });
  `);
  if(!errorMessage) {
    console.log(`
      const savedCredential = localStorage.getItem('credential');
      if(savedCredential) {
        document.getElementById('credential').value = savedCredential;
        document.getElementById('form').submit();
      }
    `);
  }
  else {
    console.log(`
      localStorage.removeItem('credential');
    `);
  }
  console.log(`
      });
    </script>
  `);
  
  writeHtmlFooter();
}


// ファイルリストページ
// ====================================================================================================

/** ファイルリストページ */
async function listFiles(inputPath) {
  const fullPath = path.resolve(rootDirectory, inputPath);
  if(!fullPath.startsWith(rootDirectory)) {
    return showErrorPage('Invalid Path');
  }
  
  const previewPath = '.' + fullPath.replace(rootDirectory, '') + '/';
  
  let dirents;
  try {
    dirents = await fs.promises.readdir(fullPath, { withFileTypes: true });
  }
  catch(error) {
    return showErrorPage('Failed To Open The Directory');
  }
  
  writeHtmlHeader('Index Of');
  console.log(`<h1>Index Of : ${previewPath}</h1>`);
  console.log('<ul>');
  if(previewPath !== './') {
    console.log(`<li><a href="javascript:void(0);" onclick="exec('cd', '..');">../</a></li>`);
  }
  
  if(!dirents.length) {
    console.log(`
        <li>(No Files)</li>
      </ul>
    `);
  }
  else {
    dirents.filter(dirent => dirent.isDirectory()).sort().forEach(dirent => {
      console.log(`<li><a href="javascript:void(0);" onclick="exec('cd', '${dirent.name}');">${dirent.name}/</a></li>`);
    });
    dirents.filter(dirent => !dirent.isDirectory()).sort().forEach(dirent => {
      console.log(`<li><a href="javascript:void(0);" onclick="exec('openFile', '${dirent.name}');">${dirent.name}</a></li>`);
    });
    console.log('</ul>');
  }
  
  console.log(`
    <form action="${process.env.SCRIPT_NAME}" method="POST" id="form">
      <input type="hidden" name="credential" value="" id="credential">
      <input type="hidden" name="mode"       value="" id="mode">
      <input type="hidden" name="targetPath" value="" id="target-path">
    </form>
    <script>

function exec(mode, targetPath) {
  document.getElementById('credential' ).value = localStorage.getItem('credential');
  document.getElementById('mode'       ).value = mode;
  document.getElementById('target-path').value = '${previewPath}' + targetPath;
  document.getElementById('form').submit();
}

    </script>
  `);
  
  writeHtmlFooter();
}


// ファイルオープン
// ====================================================================================================

/** ファイルオープン */
async function openFile(inputPath) {
  const fullPath = path.resolve(rootDirectory, inputPath);
  if(!fullPath.startsWith(rootDirectory)) {
    return showErrorPage('Invalid File Path');
  }
  
  const fileName = path.basename(fullPath) || 'file.unknown';
  const extension = path.extname(fileName).toLowerCase();
  const contentType = detectContentType(extension);
  
  try {
    const file = await fs.promises.readFile(fullPath);
    process.stdout.write(`Content-Type: ${contentType}\n`);
    process.stdout.write(`Content-Disposition: ${contentType === 'application/octet-stream' ? 'attachment' : 'inline'}; filename=${fileName}\n`);
    process.stdout.write('\n');
    process.stdout.write(file);
  }
  catch(error) {
    return showErrorPage('Failed To Open File');
  }
}

/** 拡張子による Content-Type 判定 */
function detectContentType(extension) {
  // テキスト系はその場で表示できるようにする
  const typeText = [
    '.txt', '.text', '.md', '.markdown',
    '.html', '.htm', '.xml', '.xhtml', '.xhtm',
    '.js', '.mjs', '.jsx', '.ts', '.tsx', '.vue',
    '.css', '.sass', '.scss',
    '.json', '.csv', '.tsv',
    '.sh', '.bash', '.pl', '.py', '.rb', '.cgi', '.php'
  ];
  if(typeText.includes(extension)) {
    return 'text/plain';
  }
  
  // 画像系はその場で表示できるようにする
  switch(extension) {
    case '.png' : return 'image/png';
    case '.gif' : return 'image/gif';
    case '.jpg' :
    case '.jpeg': return 'image/jpeg';
    case '.svg' : return 'image/svg+xml';
    case '.webp': return 'image/webp';
    case '.ico' : return 'image/vnd.microsoft.icon';
    case '.bmp' : return 'image/bmp';
    case '.tif' :
    case '.tiff': return 'image/tiff';
  }
  
  // それ以外の拡張子はファイルダウンロードにする
  return 'application/octet-stream';
}


// メイン
// ====================================================================================================

(async () => {
  try {
    if(process.env.REQUEST_METHOD === 'POST') {
      let rawPostBody = '';
      for await(const chunk of process.stdin) { rawPostBody += chunk; }
      const postBody = [...new URLSearchParams(rawPostBody)].reduce((acc, pair) => ({...acc, [pair[0]]: pair[1]}), {});
      
      if(postBody.credential !== credential) {
        return showLoginPage('Invalid Credential');
      }
      
      if(postBody.mode === 'login') {
        return await listFiles('./');  // ログイン直後
      }
      else if(postBody.mode === 'cd') {
        return await listFiles(postBody.targetPath);
      }
      else if(postBody.mode === 'openFile') {
        return await openFile(postBody.targetPath);
      }
      return showErrorPage('Invalid Mode');
    }
    else {
      return showLoginPage();  // GET 時はログインページを表示する
    }
  }
  catch(error) {
    console.log('Content-Type: text/html; charset=UTF-8\n\n');
    console.log('<pre style="color: #f00; font-weight: bold;">An Error Occurred :<br>', error, '</pre>');
  };
})();
