import ast

with open('models.py', 'r', encoding='utf-8') as f:
    raw = f.read()

unescaped = raw.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
with open('models.py', 'w', encoding='utf-8') as out:
    out.write(unescaped)

ast.parse(unescaped)
print('UNESCAPED AST PARSE 100% SUCCESSFUL!')
