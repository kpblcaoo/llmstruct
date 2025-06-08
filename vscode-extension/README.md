# VSCode-плагин для llmstruct (private MVP)

## Описание

Этот плагин добавляет AI-ассистента llmstruct в VSCode: чат, интеллектуальные подсказки, автодополнение и навигация по проекту на основе struct.json и LLM.

## Установка (private/manual)

1. Клонируйте или скачайте репозиторий llmstruct (или только папку vscode-extension).
2. Откройте папку `vscode-extension` в VSCode.
3. Установите зависимости:
   ```bash
   npm install
   ```
4. Соберите VSIX-пакет:
   ```bash
   npm run package
   ```
   (Если команда не работает — установите [vsce](https://code.visualstudio.com/api/working-with-extensions/publishing-extension#packaging-extensions) глобально: `npm install -g vsce`)
5. Установите расширение в VSCode:
   - Через меню: Extensions → Install from VSIX... → выбрать созданный `.vsix` файл
   - Или через терминал:
     ```bash
     code --install-extension <имя-файла>.vsix
     ```

## Настройка

- В настройках VSCode (`Ctrl+,` → Extensions → llmstruct):
  - `llmstruct.backendUrl` — адрес backend (например, `http://localhost:8000`)
  - `llmstruct.apiKey` — API-ключ (если требуется)

## Использование

- Откройте боковую панель "llmstruct Assistant" для чата с ассистентом.
- Задавайте вопросы по коду, получайте подсказки, используйте автодополнение.

## Важно
- Первая версия не публикуется в marketplace, распространяется только вручную.
- Все вопросы и баги — напрямую разработчику.

---

_Для разработчиков: см. best practices в `.cursor/rules/vscode_plugin.md`_ 