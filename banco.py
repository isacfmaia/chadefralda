import sqlite3

# Conecte ao banco de dados (ou crie se não existir)
conn = sqlite3.connect('fraldas.db')
cursor = conn.cursor()

# Crie a tabela de estoque de fraldas (se já não existir)
cursor.execute('''
CREATE TABLE IF NOT EXISTS estoque (
    tamanho TEXT PRIMARY KEY,
    quantidade INTEGER
)
''')

# Insira os tamanhos de fraldas e suas quantidades iniciais
cursor.executemany('''
INSERT OR IGNORE INTO estoque (tamanho, quantidade) VALUES (?, ?)
''', [
    ('RN', 1),
    ('P', 5),
    ('M', 15),
    ('G', 25),
    ('XG', 30),
    ('XXG', 30)
])

# Crie a tabela para registrar as respostas dos convidados
cursor.execute('''
CREATE TABLE IF NOT EXISTS convidados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    adultos INTEGER,
    criancas INTEGER,
    tamanho_fralda TEXT
)
''')

# Salve as mudanças e feche a conexão
conn.commit()
conn.close()
