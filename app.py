from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

def get_db_connection():
    conn = sqlite3.connect('fraldas.db')
    conn.row_factory = sqlite3.Row
    return conn
    
# Função de login simples
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'senha123':  # Substitua por suas credenciais
            session['logged_in'] = True
            return redirect(url_for('convidados'))
        else:
            flash('Credenciais inválidas!')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Função de logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Página protegida por autenticação
@app.route('/convidados', methods=['GET'])
def convidados():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    nome = request.args.get('nome', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    conn = get_db_connection()
    
    if nome:
        query = "SELECT * FROM convidados WHERE nome LIKE ? LIMIT ? OFFSET ?"
        convidados = conn.execute(query, ('%' + nome + '%', per_page, (page - 1) * per_page)).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM convidados WHERE nome LIKE ?", ('%' + nome + '%',)).fetchone()[0]
    else:
        query = "SELECT * FROM convidados LIMIT ? OFFSET ?"
        convidados = conn.execute(query, (per_page, (page - 1) * per_page)).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM convidados").fetchone()[0]
    
    conn.close()

    return render_template('convidados.html', convidados=convidados, total=total, page=page, per_page=per_page, nome=nome)

# Exportar dados para Excel
@app.route('/exportar_excel')
def exportar_excel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    convidados = conn.execute('SELECT * FROM convidados').fetchall()
    conn.close()

    # Converter para DataFrame do Pandas
    df = pd.DataFrame(convidados)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    
    output.seek(0)
    return send_file(output, attachment_filename='convidados.xlsx', as_attachment=True)


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
        adultos = request.form['adultos']
        criancas = request.form['criancas']
        tamanho = request.form['tamanho']
        
        if not nome or not adultos or not criancas:
            flash('Por favor, preencha todos os campos!')
            return redirect(url_for('index'))
        
        try:
            adultos = int(adultos)
            criancas = int(criancas)
        except ValueError:
            flash('Quantidade de adultos e crianças devem ser números.')
            return redirect(url_for('index'))
        
        fralda = conn.execute('SELECT quantidade FROM estoque WHERE tamanho = ?', (tamanho,)).fetchone()
        
        if fralda and fralda['quantidade'] > 0:
            conn.execute('UPDATE estoque SET quantidade = quantidade - 1 WHERE tamanho = ?', (tamanho,))
            conn.execute('INSERT INTO convidados (nome, adultos, criancas, tamanho_fralda) VALUES (?, ?, ?, ?)', 
                         (nome, adultos, criancas, tamanho))
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
