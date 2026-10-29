# DEMO: markdown-review skill

Команда (stdin JSON):

```
# пример успешной проверки (ожидается минимум ошибок)
 echo '{
   "target_paths": "docs/**/*.md",
   "required_sections": ["Требования (practice_04)"]
 }' | python3 practices/practice_04/skill/markdown_review_runner.py --stdin

# пример ошибочного ввода
 echo '{}' | python3 practices/practice_04/skill/markdown_review_runner.py --stdin
```

Фактический вывод (зафиксировано при запуске):

Успех:
```
{"issues": [{"type": "broken_link", "file": "docs/requirements.md", "line": 33, "message": "Broken local link to 'relative/path.md'"}], "summary": {"broken_link": 1, "unclosed_code_block": 0, "missing_section": 0}}
```

Ошибка ввода:
```
{"error": {"code": "INVALID_INPUT", "message": "target_paths is required"}}
```
