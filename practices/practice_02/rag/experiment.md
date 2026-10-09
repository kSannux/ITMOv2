# RAG

Файл ведёт OpenCode по вашим запросам. Агент записывает фактические результаты экспериментов и вносит изменения в связанные файлы. Свою оценку сообщайте ему в чате; вручную заполнять шаблон не нужно.

- Вопрос к источникам:

Какие явные требования к структуре ответа ассистента и проверкам подтверждают TO BE в analysis.md? Приведи цитаты с файлами и строками. Что не подтверждается источниками?

## Разрешённые источники

| Файл или документ | Зачем нужен | Какой фрагмент используем |
|---|---|---|
| practices/practice_01/product_management.md | Формат ответа и ограничение risks | Строки 7, 20, 43, 49: summary/risks≤3/file:line:evidence/checks; 422 при отсутствии diff |
| practices/practice_01/tests_e2e.md | Подтверждение структуры результата | Строка 7: summary, до 3 risks с file/line/evidence, checks |
| practices/practice_01/tests_integration.md | Подтверждение 422 и поля comment | Строка 7: 422; строка 8: ответ содержит {"comment": mock} |
| practices/practice_01/context.md | Правила доказательности | Строки 20–21, 26–33: до 3 рисков, file:line, evidence — цитата из diff; без предположений |
| practices/practice_01/TRAINING_PR.diff | Evidence AS IS для KeyError | Строки 35–38: обращение payload["diff"] → KeyError при отсутствии поля |

## Запрос


## Ответ со ссылками на источники

Подтверждённые требования (структура ответа ассистента)
- product_management.md:7 → «пользователь получает краткое summary, не более 3 проверяемых рисков с ссылками на строки и список проверок.»
- product_management.md:20 → «Ответ API: JSON с полем comment, внутри comment структура summary, risks (<=3) с file/line/evidence, checks»
- product_management.md:43 → «Then ассистент возвращает Summary, до 3 Risks с file/line/evidence, и Checks»
- tests_e2e.md:7 → «Ассистент возвращает Summary, до 3 Risks с file/line/evidence, и Checks»
- context.md:20–21 → «Помощник возвращает: 1) краткое описание изменения; 2) до трёх рисков с файлом и строкой; 3) список воспроизводимых проверок.»; «Выводы должны подтверждаться фрагментом diff или явным источником.»
- context.md:26–33 → «Результат по умолчанию: список из 3 пунктов — описание, до 3 рисков (file:line, обоснование), и проверки для запуска.»; «Запрещены предположения без ссылки на diff/источник.»
- tests_integration.md:8 → «Ответ сервиса содержит {"comment": mock}»

Подтверждённые проверки
- product_management.md:49; tests_integration.md:7; tests_e2e.md:8 → отсутствие diff → TO BE: 422 (AS IS: 500)
- context.md:38–41 → «… payload["diff"] вызывает KeyError … Проверка: отправить POST /api/reviews с пустым JSON …»
- TRAINING_PR.diff:35–38 → обращение к payload["diff"] (evidence для негативного сценария)

Неподтверждённые пункты
- Точная схема JSON сверх перечисленных полей; формат ссылок/строк; структура checks как {action, expected}; «один top-level key comment»; Content-Type: application/json — прямых цитат нет.

Вывод: TO BE подтверждён артефактами в части структуры comment{summary, risks≤3(file/line/evidence), checks} и 422 при невалидном diff; детали форматов вне этого списка источниками не закреплены.
## Что изменили в исходном артефакте

- Файл и раздел: practices/practice_01/analysis.md — раздел TO BE (ссылки на источники)
- Изменение: добавлен подраздел «Ссылки на источники (RAG)» с перечислением подтверждающих артефактов и их содержания
- Как проверили ссылки: сопоставили цитаты из product_management.md, tests_e2e.md, tests_integration.md, context.md и TRAINING_PR.diff с формулировками TO BE
- Что отклонили как неподтверждённое: детали форматов сверх перечисленных полей (точная схема JSON, формат line/file, Content-Type)
