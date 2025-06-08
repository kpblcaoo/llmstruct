import * as vscode from 'vscode';
import { Buffer } from 'buffer';

class LLMStructAssistantViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'llmstruct-assistant-view';

  constructor(private readonly _extensionUri: vscode.Uri) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken,
  ) {
    const config = vscode.workspace.getConfiguration('llmstruct');
    const backendUrl = config.get<string>('backendUrl', 'http://localhost:8000');
    const apiKey = config.get<string>('apiKey', '');

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri]
    };

    webviewView.webview.html = this._getHtmlContent(webviewView.webview, backendUrl, apiKey);

    // Обработка сообщений от webview
    webviewView.webview.onDidReceiveMessage(async (msg: any) => {
      if (msg.type === 'pickProjectDir') {
        const folderUri = await vscode.window.showOpenDialog({
          canSelectFolders: true,
          canSelectFiles: false,
          canSelectMany: false,
          openLabel: 'Выбрать папку проекта'
        });
        if (folderUri && folderUri[0]) {
          webviewView.webview.postMessage({ type: 'setProjectDir', dirPath: folderUri[0].fsPath });
        }
      }
      if (msg.type === 'analyze') {
        const dirPath = msg.dirPath;
        if (!dirPath) {
          webviewView.webview.postMessage({ type: 'analyzeResult', error: 'Не указан путь к проекту!' });
          return;
        }
        try {
          const resp = await fetch(`${backendUrl}/api/v1/parse`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${apiKey}`,
            },
            body: JSON.stringify({
              root_dir: dirPath,
              include: ['*.py'],
              exclude: ['tests/*'],
              include_ranges: true,
              use_cache: false,
            }),
          });
          if (!resp.ok) throw new Error(`Ошибка: ${resp.status}`);
          const data = await resp.json();
          const structJson = JSON.stringify(data.struct, null, 2);
          const fileUri = vscode.Uri.joinPath(vscode.Uri.file(dirPath), 'struct.json');
          await vscode.workspace.fs.writeFile(fileUri, Buffer.from(structJson, 'utf8'));
          webviewView.webview.postMessage({ type: 'analyzeResult', success: true });
        } catch (e) {
          webviewView.webview.postMessage({ type: 'analyzeResult', error: String(e) });
        }
      }
    });
  }

  private _getHtmlContent(webview: vscode.Webview, backendUrl: string, apiKey: string): string {
    const nonce = getNonce();
    return `<!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}'; connect-src *;">
          <title>llmstruct Assistant</title>
          <style>
            body { font-family: sans-serif; padding: 10px; }
            #chat { height: 300px; overflow-y: auto; border: 1px solid #444; padding: 8px; margin-bottom: 8px; background: #181818; color: #eee; }
            .msg-user { color: #8ec07c; margin-bottom: 4px; }
            .msg-bot { color: #b8bb26; margin-bottom: 8px; }
            #input-row { display: flex; gap: 4px; }
            #user-input { flex: 1; }
            button { background: #458588; color: #fff; border: none; padding: 6px 12px; border-radius: 3px; cursor: pointer; }
            button:disabled { opacity: 0.5; }
            #analyze-btn { margin-bottom: 8px; width: 100%; }
            #project-dir-row { display: flex; gap: 4px; margin-bottom: 8px; }
            #project-dir { flex: 1; }
            #pick-dir-btn { width: 32px; }
          </style>
        </head>
        <body>
          <h2>llmstruct Assistant</h2>
          <div id="project-dir-row">
            <input id="project-dir" type="text" placeholder="Путь к проекту..." />
            <button id="pick-dir-btn" title="Выбрать папку">📁</button>
          </div>
          <button id="analyze-btn">Анализировать код (struct.json)</button>
          <div id="chat"></div>
          <div id="input-row">
            <input id="user-input" type="text" placeholder="Введите сообщение..." />
            <button id="send-btn">Отправить</button>
          </div>
          <script nonce="${nonce}">
            const chat = document.getElementById('chat');
            const input = document.getElementById('user-input');
            const btn = document.getElementById('send-btn');
            const analyzeBtn = document.getElementById('analyze-btn');
            const projectDirInput = document.getElementById('project-dir');
            const pickDirBtn = document.getElementById('pick-dir-btn');
            const backendUrl = "${backendUrl}";
            const apiKey = "${apiKey}";
            const vscode = acquireVsCodeApi();

            function appendMsg(text, who) {
              const div = document.createElement('div');
              div.className = who === 'user' ? 'msg-user' : 'msg-bot';
              div.textContent = text;
              chat.appendChild(div);
              chat.scrollTop = chat.scrollHeight;
            }

            btn.onclick = async () => {
              const msg = input.value.trim();
              if (!msg) return;
              appendMsg('Вы: ' + msg, 'user');
              input.value = '';
              btn.disabled = true;
              try {
                const headers = { 'Content-Type': 'application/json' };
                if (apiKey) headers['Authorization'] = 'Bearer ' + apiKey;
                const resp = await fetch(backendUrl + '/api/v1/chat/message', {
                  method: 'POST',
                  headers,
                  body: JSON.stringify({ content: msg })
                });
                if (!resp.ok) {
                  let errText = 'Ошибка сети: ' + resp.status;
                  try { const err = await resp.json(); if (err.detail) errText += ' — ' + err.detail; } catch {}
                  throw new Error(errText);
                }
                const data = await resp.json();
                appendMsg('Ассистент: ' + (data.content || '[нет ответа]'), 'bot');
              } catch (e) {
                appendMsg('Ошибка: ' + e, 'bot');
              } finally {
                btn.disabled = false;
              }
            };
            input.addEventListener('keydown', e => { if (e.key === 'Enter') btn.onclick(); });

            analyzeBtn.onclick = () => {
              const dirPath = projectDirInput.value.trim();
              if (!dirPath) {
                appendMsg('Укажите путь к проекту!', 'bot');
                return;
              }
              vscode.postMessage({ type: 'analyze', dirPath });
            };

            pickDirBtn.onclick = () => {
              vscode.postMessage({ type: 'pickProjectDir' });
            };

            window.addEventListener('message', event => {
              const msg = event.data;
              if (msg.type === 'setProjectDir') {
                projectDirInput.value = msg.dirPath;
              }
              if (msg.type === 'analyzeResult') {
                if (msg.success) {
                  appendMsg('struct.json успешно создан!', 'bot');
                } else {
                  appendMsg('Ошибка анализа: ' + (msg.error || ''), 'bot');
                }
              }
            });
          </script>
        </body>
      </html>`;
  }
}

function getNonce() {
  let text = '';
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for (let i = 0; i < 16; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}

export function activate(context: vscode.ExtensionContext) {
  console.log('Activating llmstruct Assistant extension...');

  try {
    const provider = new LLMStructAssistantViewProvider(context.extensionUri);
    
    // Register the webview provider
    const registration = vscode.window.registerWebviewViewProvider(
      LLMStructAssistantViewProvider.viewType,
      provider,
      {
        webviewOptions: {
          retainContextWhenHidden: true
        }
      }
    );

    context.subscriptions.push(registration);
    console.log('WebView provider registered successfully');

    // Show activation message
    vscode.window.showInformationMessage('llmstruct Assistant активирован!');
  } catch (error) {
    console.error('Error during activation:', error);
    vscode.window.showErrorMessage(`Ошибка активации llmstruct Assistant: ${error}`);
  }
}

export function deactivate() {
  console.log('Deactivating llmstruct Assistant extension...');
} 