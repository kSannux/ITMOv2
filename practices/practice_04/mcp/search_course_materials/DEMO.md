# DEMO: search_course_materials MCP

CLI (stdin JSON):

```
echo '{
  "query": "Практика",
  "include": "README.md",
  "limit": 3
}' | python3 practices/practice_04/mcp/search_course_materials/server.py --stdin
```

Фактический успех (зафиксировано при запуске):
```
{"results": [{"path": "README.md", "line": 45, "snippet": "Лекция и практика проходят раз в неделю: день лекции, ден…"}, {"path": "README.md", "line": 51, "snippet": "**Практика 1. Проект: знакомим с техническими бизн…"}, {"path": "README.md", "line": 65, "snippet": "**Практика 2. Дорабатываем артефакты для программи…"}], "meta": {"query": "Практика", "count": 3, "truncated": true}}
```

Ошибка (короткий query):
```
echo '{"query":"a","include":"README.md"}' | python3 practices/practice_04/mcp/search_course_materials/server.py --stdin
```
Результат:
```
{"error": {"code": "INVALID_INPUT", "message": "query must be a non-empty string of length >= 2"}}
```

StdIO MCP-сервер:

```
python3 practices/practice_04/mcp/search_course_materials/mcp_server.py
```

Дальнейшее подключение — через клиент MCP (например, OpenCode), согласно конфигурации в opencode.json.
