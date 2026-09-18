---
name: Generated source templates
description: Non-obvious escaping rules for Python source emitted from the built-in provider's outer f-string
---

## Rule
When `_gen_code()` emits Python through an outer f-string, double braces only for braces that must survive into a generated inner f-string. Ordinary generated expressions such as `rec.name` must remain plain text, while generated `\n` escapes need an extra backslash so the outer template does not turn them into literal newlines.

**Why:** A missing outer escape evaluates a generated variable during generation; an over-escape changes normal Python expressions into set expressions, and an unescaped newline can make the generated source syntactically invalid.

**How to apply:** After changing the template, generate a temporary project, compile both source and tests, run `main.py --help`, and exercise at least one real CRUD flow.