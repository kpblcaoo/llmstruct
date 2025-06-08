import * as vscode from 'vscode';

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

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri]
    };

    webviewView.webview.html = this._getHtmlContent(webviewView.webview, backendUrl);
  }

  private _getHtmlContent(webview: vscode.Webview, backendUrl: string): string {
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
          </style>
        </head>
        <body>
          <h2>llmstruct Assistant</h2>
          <div id="chat"></div>
          <div id="input-row">
            <input id="user-input" type="text" placeholder="Введите сообщение..." />
            <button id="send-btn">Отправить</button>
          </div>
          <script nonce="${nonce}">
            const chat = document.getElementById('chat');
            const input = document.getElementById('user-input');
            const btn = document.getElementById('send-btn');
            const backendUrl = "${backendUrl}";
            // Получаем apiKey из настроек расширения через postMessage
            let apiKey = '';
            window.addEventListener('message', event => {
              if (event.data && event.data.type === 'llmstruct-api-key') {
                apiKey = event.data.value || '';
              }
            });
            // Запрашиваем apiKey у расширения
            window.parent.postMessage({ type: 'llmstruct-get-api-key' }, '*');

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