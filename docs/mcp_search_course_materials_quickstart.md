# Инструкция: запуск и проверка MCP search_course_materials

Задача
- Прочитать AGENTS.md и следовать указанному runner'у.
- Найти через подключённый MCP search_course_materials упоминания "Практика" в README.md.
- Проверить документацию подключённым markdown-review skill'ом на docs/**/*.md с обязательным разделом "Требования (practice_04)".

Шаг 1. Прочитай AGENTS.md
- Проверка выполняется одной командой: sh scripts/check.sh
- Skill:
  - Док: practices/practice_04/skill/markdown-review/SKILL.md
  - ДЕМО: practices/practice_04/skill/markdown-review/DEMO.md
  - Runner: practices/practice_04/skill/markdown_review_runner.py
- MCP:
  - Локальный stdio-сервер: practices/practice_04/mcp/search_course_materials/mcp_server.py
  - Конфигурация: opencode.json → mcp.servers.search_course_materials (type: local, command с .venv/bin/python)

Шаг 2. Найди сведения через MCP (подключённый search_course_materials)
- В OpenCode вызови инструмент search_course_materials.search с параметрами: query="Практика", include="README.md", limit=3.
- Фактический результат:
  {"results": [{"path": "README.md", "line": 45, "snippet": "Лекция и практика проходят раз в неделю: день лекции, ден..."}, {"path": "README.md", "line": 51, "snippet": "**Практика 1. Проект: знакомим с техническими бизн..."}, {"path": "README.md", "line": 65, "snippet": "**Практика 2. Дорабатываем артефакты для программи..."}], "meta": {"query": "Практика", "count": 3, "truncated": true}}

Шаг 3. Проверь Markdown подключённым skill'ом markdown-review
- Вызови skill согласно SKILL.md (или используй runner): target_paths="docs/**/*.md", required_sections=["Требования (practice_04)"].
- Результат проверки:
  {"issues": [{"type": "broken_link", "file": "docs/requirements.md", "line": 33, "message": "Broken local link to 'relative/path.md'"}], "summary": {"broken_link": 1, "unclosed_code_block": 0, "missing_section": 0}}

Шаг 4. Результат hook после правки
- См. журнал: practices/practice_04/artifacts/hook.log
- Фактические записи (последние строки):
  2026-10-09T07:27:07.946Z tool=patch exit=2
  2026-10-09T07:28:21.609Z tool=patch exit=2

Примечание
- Команды и результаты приведены из фактических запусков в репозитории. Значения line/snippet/summary и коды выхода hook могут меняться при обновлении контента.
