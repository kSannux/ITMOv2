# R.C.T.F.

Файл ведёт OpenCode по вашим запросам. Агент записывает фактические результаты экспериментов и вносит изменения в связанные файлы. Свою оценку сообщайте ему в чате; вручную заполнять шаблон не нужно.

- **Role:** Старший ревьюер SDLC и промпт-инженер
- **Context:** practices/practice_01/analysis.md; цель — уточнить TO BE, диаграмму и критерии проверяемости без противоречий с context.md, product_management.md и tests_*
- **Task:** Аудит TO BE/диаграммы/таблицы «Разница» на проверяемость и согласованность; предложить минимальные уточнения с явными проверками
- **Format:** Findings, Recommendations, Checks, Limitations (кратко; готовые вставки Markdown)

## Полный запрос

Role:
- Senior SDLC Reviewer and Prompt Engineer.

Context:
- Target artifact: practices/practice_01/analysis.md (Анализ процесса: AS IS и TO BE).
- Goal: уточнить TO BE, диаграмму и критерии проверяемости; формулировки должны быть проверяемыми и непротиворечивыми относительно связанных артефактов (context.md, product_management.md, tests_*).
- Current TO BE/Diagram/Table — как принято в результате Few-shot.
- Constraints: не вводить новых требований вне учебного кейса; не менять файлы; вернуть готовые вставки.

Task:
- Audit the TO BE section, Mermaid diagram, and «Разница» table for testability, ambiguity, and cross-artifact consistency.
- Propose precise, minimal refinements with explicit verification steps, tagged [Unit]/[Integration]/[E2E].

Format:
- Findings, Recommendations (insert/replace snippets), Checks (Given/When/Then), Limitations.

## Что получили

Findings
- Поле line неформализовано: неясно формат значения (число/диапазон), нумерация (0/1-базовая), сторона diff (+/-).
- Структура checks не зафиксирована на уровне ключей (только «шаги и ожидаемые результаты» в тексте).
- Успешный статус/Content-Type ответа не уточнены (ожидается 200 и application/json).
- Требование «evidence — цитата из diff» неформализовано как проверяемое правило (должно быть буквальное вхождение).
- Источник поля file не уточнен (должен соответствовать пути из заголовка +++ в unified diff).
- Mermaid не фиксирует код 200 для успешного ответа; «Сбор ответа» не указывает нормализацию (ограничение risks ≤3, обязательные поля).
- Таблица «Разница» не покрывает явные правила для checks-структуры и формата line/file/evidence.

Recommendations
- TO BE → Выход (уточнить risks):
  - risks: массив ≤3; каждый элемент: file (путь из строки +++ новой версии файла), line (строка формата N или N-M, 1-базовая, по стороне «+»), evidence (дословная цитата из diff).
- TO BE → Выход (уточнить checks):
  - checks: массив объектов; каждый элемент: action (шаг), expected (ожидаемый результат); строки непустые.
- TO BE → Валидация/Ответ:
  - Успех: 200 OK, Content-Type: application/json; Ошибка валидации diff (отсутствует/не str): 422 Unprocessable Entity (стандарт FastAPI).
- TO BE → Обработка/Нормализация:
  - ReviewService возвращает ровно один верхний ключ comment; гарантирует наличие summary: str, risks: [], checks: []; обрезает risks до 3; evidence — подстрока diff.
- Mermaid (замена блока I и уточнение H):
  - H: «Сбор и нормализация: summary, risks≤3(file/line/evidence), checks(action/expected)»
  - I: «HTTP 200 JSON {comment: {...}}»
- Таблица «Разница» (добавить строки):
  - Код успеха/Content-Type | Не зафиксировано | 200 + application/json | E2E позитив: статус 200; JSON с comment
  - Структура checks | Не детализирована | Каждый check: {action, expected} | E2E: у каждого check два поля; не пустые
  - Формат line/file/evidence | Не детализировано | line: N или N-M; file из +++; evidence — подстрока diff | Unit/Integration: см. Checks C2–C3

Checks
- [Integration] Валидация diff отсутствует
  - Given POST /api/reviews с телом {}
  - When отправляем запрос
  - Then статус 422; тело содержит detail; см. P1-02 Checks C1
- [E2E] Позитивный сценарий
  - Given валидный unified diff и Content-Type application/json
  - When POST /api/reviews с { "diff": "..." }
  - Then статус 200; top-level только comment; внутри summary: string, risks: array ≤3, checks: array; см. P1-02 результат
- [Unit] Формирование промпта
  - Given diff="---diff---"
  - When ReviewService.review(diff)
  - Then prompt содержит "Review this pull request and find problems:\n---diff---"; см. P1-02
- [Unit] Нормализация и ограничение risks
  - Given LLM вернул >3 рисков
  - When ReviewService нормализует ответ
  - Then в comment.risks ровно 3 элемента (первые три по порядку)
- [Unit] Формат line и evidence
  - Given comment.risks[i]
  - When проверяем line
  - Then line соответствует ^\\d+(?:-\\d+)?$; evidence — дословная подстрока исходного diff
- [Integration] Соответствие file путям из diff
  - Given diff с файлами в заголовках +++
  - When POST /api/reviews и получаем comment.risks
  - Then каждый risk.file совпадает с одним из путей из +++; несоответствие — тест падает
- [E2E] Структура checks
  - Given валидный diff
  - When POST /api/reviews
  - Then каждый элемент comment.checks — объект с полями action и expected; обе строки непустые; см. P1-02 Checks

Limitations
- Не зафиксированы правила для пустого diff и максимального размера diff — остаётся открытым вопросом.
- Не определены требования к локализации/языку текста summary/risks/checks.
- Не описана стратегия при несоответствии LLM-ответа (кроме нормализации) — например, политики ошибок/трейсинга.

## Что изменили в исходном артефакте

- Файл и раздел: practices/practice_01/analysis.md — раздел TO BE, диаграмма Mermaid и таблица «Разница»
- Изменение: уточнили ограничения, подтверждённые источниками — risks≤3 и evidence как цитата; скорректировали формулировки и диаграмму (без неподтверждённых деталей); предложения по Content-Type/формату line/file/структуре checks вынесены как черновики и позже отклонены Chain of Verification
- Как проверили: сопоставили с context.md, product_management.md и tests_*; проверки из раздела Checks (Integration 422; E2E — формат comment; Unit — промпт/нормализация)
- Что отклонили: Content-Type application/json, «один top-level key comment», точный формат line/file, структура checks {action, expected} (отклонены CoV как без явных источников)
