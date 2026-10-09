# Журнал экспериментов Практики 2

Файл ведёт OpenCode по вашим запросам. Агент записывает фактические результаты экспериментов и вносит изменения в связанные файлы. Свою оценку сообщайте ему в чате; вручную заполнять шаблон не нужно.

- Выбранный слабый артефакт Практики 1: practices/practice_01/analysis.md — уточнение TO BE, диаграммы и критериев проверяемости
- Что в нём нужно улучшить: уточнить раздел TO BE и таблицу «Разница», синхронизировать диаграмму с TO BE, добавить воспроизводимые «Как проверим изменение» для каждого пункта
- Как поймём, что изменение полезно: make step2 OK; формулировки стали проверяемыми и не противоречат context.md, product_management.md и tests_*; диаграмма согласована с TO BE

| Техника | Файл эксперимента | Изменённый файл Практики 1 | Конкретное изменение | Проверка | Что отклонили |
|---|---|---|---|---|---|
| Few-shot | [`few_shot/experiment.md`](few_shot/experiment.md) | practices/practice_01/analysis.md | Уточнили TO BE (валидация diff→422; comment{summary, risks≤3(file/line/evidence), checks}); обновили диаграмму и «Разница» | Визуальная проверка согласованности с context.md и product_management.md; make step2 — после всех техник | Расплывчатые формулировки и диаграмма без валидации/422 |
| R.C.T.F. | [`rctf/experiment.md`](rctf/experiment.md) | practices/practice_01/analysis.md | Уточнили ограничения: risks≤3, evidence — цитата; скорректировали диаграмму; исключили неподтверждённые детали | Checks: Integration 422; E2E — формат comment; Unit — промпт/нормализация | Content-Type, формат line/file, структура checks {action, expected} (перенесены в предложения, не закреплены) |
| Chain of Verification | [`chain_of_verification/experiment.md`](chain_of_verification/experiment.md) | practices/practice_01/analysis.md | Сохранили только подтверждённые источниками части TO BE; отклонили неподтверждённые уточнения | Таблица CoV: ссылки на product_management.md, tests_e2e.md, tests_integration.md, context.md | Content-Type, «один top-level key», точный формат line/file, {action, expected} |
| Tree of Thoughts | [`tree_of_thoughts/experiment.md`](tree_of_thoughts/experiment.md) | practices/practice_01/analysis.md | Добавили мягкую рекомендацию «подсказка в скобках» для пунктов TO BE | Проверка: не меняет tests_*; CoV использует для ручной верификации | Жёсткие форматы/требования без источников |
| RAG | [`rag/experiment.md`](rag/experiment.md) | practices/practice_01/analysis.md | Добавили подраздел «Ссылки на источники (RAG)» с перечислением подтверждающих артефактов | Сопоставление цитат с TO BE; ссылки на product_management.md, tests_e2e.md, tests_integration.md, context.md, TRAINING_PR.diff | Детали форматов сверх перечисленных полей |
| ReAct | [`react/experiment.md`](react/experiment.md) | practices/practice_01/analysis.md | Добавили примечание о согласованности TO BE с другими артефактами | Наблюдаемые шаги 1–5: чтение файлов и сопоставление; противоречий не найдено | — |
