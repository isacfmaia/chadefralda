from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Substitua por uma chave secreta

def get_db_connection():
    conn = sqlite3.connect('fraldas.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/sucesso')
def sucesso():
    nome = request.args.get('nome')
    tamanho = request.args.get('tamanho')
    return render_template('sucesso.html', nome=nome, tamanho=tamanho)

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    
    if request.method == 'POST':
        nome = request.form['nome']
        acompanhantes = request.form['acompanhantes']
        tamanho = request.form['tamanho']
        
        if not nome or not acompanhantes:
            flash('Por favor, preencha todos os campos!')
            return redirect(url_for('index'))
        
        try:
            acompanhantes = int(acompanhantes)
        except ValueError:
            flash('Quantidade de acompanhantes deve ser um número.')
            return redirect(url_for('index'))
        
        fralda = conn.execute('SELECT quantidade FROM estoque WHERE tamanho = ?', (tamanho,)).fetchone()
        
        if fralda and fralda['quantidade'] > 0:
            conn.execute('UPDATE estoque SET quantidade = quantidade - 1 WHERE tamanho = ?', (tamanho,))
            conn.execute('INSERT INTO convidados (nome, acompanhantes, tamanho_fralda) VALUES (?, ?, ?)', 
                         (nome, acompanhantes, tamanho))
            conn.commit()
            return redirect(url_for('sucesso', nome=nome, tamanho=tamanho))
        else:
            flash(f'O tamanho {tamanho} está esgotado.')
            return redirect(url_for('index'))
    
    fraldas = conn.execute('SELECT * FROM estoque').fetchall()
    conn.close()
    
    return render_template('index.html', fraldas=fraldas)

if __name__ == '__main__':
    app.run(debug=True)