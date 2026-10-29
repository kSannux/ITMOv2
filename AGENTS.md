Среда агента (practice_04)

- Контекст и контракт:
  - Агент читает требования из docs/requirements.md и следует им.
  - Проверка выполняется одной командой: sh scripts/check.sh (pytest).

- Skill: markdown-review
  - Назначение: проверка Markdown-файлов на битые локальные ссылки, незакрытые блоки кода и недостающие разделы.
  - Документация: practices/practice_04/skill/markdown-review/SKILL.md
  - Демонстрация: practices/practice_04/skill/markdown-review/DEMO.md (содержит успешный и ошибочный кейсы с фактическим выводом).
  - Runner (CLI): practices/practice_04/skill/markdown_review_runner.py
    - Пример: echo '{"target_paths":"docs/**/*.md","required_sections":["Требования (practice_04)"]}' | python3 practices/practice_04/skill/markdown_review_runner.py --stdin

- MCP: search_course_materials (локальный stdio-сервер)
  - Назначение: поиск по материалам курса (lections/, practices/, docs/, README.md), возвращает path/line/snippet.
  - Конфигурация OpenCode (V2.0.20): opencode.json → mcp.servers.search_course_materials
    - type: local
    - command: [".venv/bin/python", "practices/practice_04/mcp/search_course_materials/mcp_server.py"]
    - cwd: "."
  - Реализация сервера: practices/practice_04/mcp/search_course_materials/mcp_server.py (на FastMCP)
  - Демонстрация CLI: practices/practice_04/mcp/search_course_materials/DEMO.md
  - Проверка подключения: opencode mcp list (ожидается connected)

- Требования к окружению
  - Python 3.11+ (или совместимый python3 в системе).
  - Рекомендуется виртуальное окружение .venv; зависимости устанавливаются командой:
    - python3 -m pip install -r requirements.txt

- Рабочий процесс агента
  1. Прочитать AGENTS.md и docs/requirements.md.
  2. Загрузить инструкции skill из SKILL.md (markdown-review).
  3. При необходимости вызывать MCP tool search_course_materials.search для уточнения контекста.
  4. После правок запускать sh scripts/check.sh и возвращать результат в чат.

- Тесты
  - tests/test_example.py — smoke-тест.
  - tests/test_search_course_materials.py — успешные и ошибочные кейсы для MCP.
  - Runner: scripts/check.sh (POSIX sh), вызывает pytest -q.

- Примечания
  - Не изменяйте контракт (docs/requirements.md) и runner (scripts/check.sh) без явного согласования.
  - MCP-сервер использует .venv/bin/python; убедитесь, что зависимости установлены в этом окружении.
