# 📋 СЛУЖЕБНАЯ ЗАПИСКА
## Вопросы для категоризации 926 элементов

**Дата**: 2025-05-29  
**От**: AI Assistant  
**Кому**: kpblc  
**Тема**: Уточнения по decision checklist перед обработкой  

---

## 🎯 СТРАТЕГИЧЕСКИЕ ВОПРОСЫ

### **GitHub vs Personal разделение:**
1. **Где граница между GitHub issues и personal management?** @kpblcaoo - по этому вопросу, думаю, попадать должно автоматически пока только то, что команда должна 100% решать сама, остальное с моего одобрения
   - Пример: "Улучшить workflow команды" → GitHub или Personal?
   - Критерий: если команда может делать без твоего постоянного участия = GitHub?

2. **Язык документации - гибридный подход ОК?** @kpblcaoo - отлично
   - Issues/comments на русском, README билингвальный?
   - Нужно ли переводить technical specs для команды? @kpblcaoo -  да.

### **Антизахламление стратегия:**
3. **Review cycle - каждые 6 месяцев реально?** @kpblcaoo -  главное - иметь протокол пересмотра архивных записей, что-то может стать актуальным
   - Автоматические напоминания нужны?
   - Кто будет делать cleanup если команда вырастет? - @kpblcaoo - может, делить доски и бекенд для них на отделы итд? мне-то точно личная доска будет нужна

4. **Versioning strategy:** @kpblcaoo -  пока не решил. у меня весрсия очень давно не обновлялась. но ещё явно не 1.0
   - v1.0 → v1.1 → v2.0 когда increment?
   - Superseded items удалять или архивировать?

---

## 📊 КАТЕГОРИЗАЦИЯ УТОЧНЕНИЯ

### **GitHub Issues (команда может делать):**
**ВОПРОС**: Что если task простой, но требует твоего review архитектуры?
- [ ] Все равно GitHub (с пометкой "needs architecture review")?
- [x] Personal management (ты координируешь)?

**Примеры для clarification:** @kpblcaoo -  для прояснения хочу сказать, что кроме модуля для бизнес-целей(комплексного) я хочу иметь модуль личного планирования, и иметь возможность его использовать в сочетании с остальными. Например мне нужно продумать возможность репатриации в Израиль и где стоит обосновать компанию. Мы с Ваней сейчас живём в РФ, Мамай в Израиле, я могу репатреироваться и позже построю план, но жить там вообще не хочу, хочу использовать как ступеньку, если это разумный шаг.
- "Добавить валидацию форм" → GitHub issues? ✅
- "Спроектировать API архитектуру" → Personal management? ✅
- "Рефакторинг core модуля" → GitHub или Personal? ❓

### **GitHub Epics (большие фичи):**
**ВОПРОС**: Минимальный размер для epic?
- 3+ связанных issues = epic? @kpblcaoo - да
- Только customer-facing features? @kpblcaoo - нет

### **Personal Tools vs GitHub:**
**ВОПРОС**: Инструменты для команды куда? @kpblcaoo - думаю, надо продумать функионал для меня и команды отдельно?
- "CI/CD pipeline setup" → GitHub issues (команда будет использовать)?
- "Personal dashboard для отслеживания прогресса команды" → Personal tools?

---

## 🔄 ДУБЛИКАТЫ И КОНФЛИКТЫ

### **Duplicate resolution strategy:**
5. **Похожие titles, разный content - как мерджить?** @kpblcaoo - откладываем для ручного ревью с помощью подсказок ии
   - Всегда manual review или есть автоматические правила?
   - Сохранять historical versions? @kpblcaoo - да

6. **Evolution одной идеи:** @kpblcaoo - ну да, как-то так
   - "AI self-awareness v1" vs "AI self-awareness v2.0" 
   - Оставить latest + архивировать старые?

### **Cross-references:**
7. **Связанные items в разных категориях - как трекать?** 
   - GitHub issue зависит от Personal management task
   - Как в metadata указывать dependencies между файлами?

---

## 🚀 T-POT DEADLINE ВОПРОСЫ

### **Завтрашний deadline:**
8. **T-Pot items priority override?** @kpblcaoo - мы должны строить эффективный план для того, чтобы и допилить необходимое для красивого и лёгкого выполнения, и успеть к дедлайну нормально.  вопросы твои тут не очень понял
   - Если T-Pot task подходит под несколько категорий, всегда → t_pot_revenue.json?
   - Или дублировать в relevant категории?

9. **Post-deployment T-Pot items:** @kpblcaoo - да
   - Maintenance tasks → GitHub issues?
   - Monetization planning → Personal management?

---

## 📁 СТРУКТУРА .PERSONAL КАТАЛОГОВ

### **Предложенная структура:**
10. **Нужны ли подкаталоги в .personal/?**

```yaml
.personal/
├── management/           # Управленческие задачи
│   ├── team_coordination/
│   ├── strategy_planning/
│   └── project_oversight/
├── tools/               # Личные инструменты
│   ├── productivity/
│   ├── automation/
│   └── dashboards/
├── learning/            # Личное развитие  
│   ├── skills/
│   ├── research/
│   └── experiments/
├── archive/             # Устаревшие решения
│   ├── 2024/
│   └── deprecated/
└── processing/          # Результаты обработки 926 items
    ├── categorized/
    ├── conflicts/
    └── reviews/
```

**ВОПРОС**: Эта структура подходит или нужна другая организация?@kpblcaoo - я думаю, нужны папки под конкретный план, как сейчас мы прорабатываем вопрос реорганизации с помощью пачки записок и планов - это должно быть очевидно связано одним каталогом

---

## ⚠️ КРИТИЧЕСКИЕ РЕШЕНИЯ НУЖНЫ

### **Перед запуском processing:**
- [ ] **Подтвердить file naming convention**
- [ ] **Утвердить metadata schema** 
- [ ] **Решить язык вопрос окончательно**
- [ ] **Выбрать versioning strategy**
- [ ] **Определить review cycle**

### **Processing параметры:**
- [x] **Similarity threshold для дубликатов** (сейчас 80%) @kpblcaoo - норм
- [ ] **Automatic categorization confidence level**
- [ ] **Manual review triggers**

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

1. **ОТВЕТИТЬ на вопросы выше** ✋
2. **Создать .personal структуру каталогов** 
3. **Обновить processing script** под окончательные решения
4. **Тест-прогон** на sample данных
5. **Full processing** 926 items

**ВАЖНО**: Не запускать processing до получения ответов на критические вопросы!

---

**Подпись**: AI Assistant  
**Статус**: Waiting for decisions  
**Next action**: Ответы + .personal structure creation 