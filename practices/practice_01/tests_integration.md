# Integration-проверки

Файл ведёт OpenCode. Обсудите с агентом содержание и проверьте предложенный diff. Все дополнения и исправления поручайте агенту в чате.

| Связь компонентов | Что может сломаться | Как воспроизводим | Ожидаемый результат | Подтверждение |
|---|---|---|---|---|
| FastAPI endpoint -> ReviewService | Отсутствует ключ diff | POST /api/reviews с {} | AS IS: 500 с KeyError; TO BE: 422 | Цитата из diff; P1-02 Checks |
| ReviewService -> LLM | Непредусмотренный ответ LLM | Mock generate, вернуть фиксированную строку | Ответ сервиса содержит {"comment": mock} | Логика review_service.review |

## Как использовали AI

 - Для чего: зафиксировать интеграционные сценарии FastAPI↔ReviewService и ReviewService↔LLM на основе diff.
 - Строка в [`prompts.md`](prompts.md): P1-03
- Что проверил студент и какие исправления поручил агенту: сценарии интеграции согласованы с diff и P1-02; формат ответа API уточнён как JSON с comment{summary, risks, checks}.
