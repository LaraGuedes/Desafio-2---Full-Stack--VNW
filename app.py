from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def init_db():
    try:
        with sqlite3.connect('database.db') as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS livros(
                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                             titulo TEXT NOT NULL,
                             categoria TEXT NOT NULL,
                             autor TEXT NOT NULL,
                             imagem_url TEXT NOT NULL
                             )
                             """)
            print("Banco de dados inicializado com sucesso!!")
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")

init_db()

@app.route('/')
def homepage():
    return "Bem-vindo à API de Livros!"  

@app.route("/doar", methods=['POST'])
def doar():
    try:
        dados = request.get_json()

        titulo = dados.get("titulo")
        categoria = dados.get("categoria")
        autor = dados.get("autor")
        imagem_url = dados.get("imagem_url")

        if not all([titulo, categoria, autor, imagem_url]):
            return jsonify({'erro': 'Todos os campos são obrigatórios', 
                            'campos_faltando': {
                                'titulo': titulo is None,
                                'categoria': categoria is None,
                                'autor': autor is None,
                                'imagem_url': imagem_url is None
                            }}), 400

        with sqlite3.connect('database.db') as conn:
            conn.execute(""" INSERT INTO livros (titulo, categoria, autor, imagem_url)
                             VALUES(?,?,?,?)""", (titulo, categoria, autor, imagem_url))
            conn.commit()

        return jsonify({'mensagem': 'Livro cadastrado com sucesso'}), 201

    except sqlite3.Error as e:
        return jsonify({'erro': f'Erro ao cadastrar livro: {e}'}), 500

@app.route('/livros', methods=['GET'])
def listar_livros():
    try:
        with sqlite3.connect('database.db') as conn:
            livros = conn.execute("SELECT * FROM livros").fetchall()

        livros_formatados = []

        for livro in livros:
            dicionario_livros = {
                "id": livro[0],
                "titulo": livro[1],
                "categoria": livro[2],
                "autor": livro[3],
                "imagem_url": livro[4]
            }
            livros_formatados.append(dicionario_livros)

        return jsonify(livros_formatados)

    except sqlite3.Error as e:
        return jsonify({'erro': f'Erro ao listar livros: {e}'}), 500

@app.route('/livros/<int:livro_id>', methods=['DELETE'])
def deletar_livro(livro_id):
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
            conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"erro": "Livro não encontrado"}), 400

        return jsonify({"mensagem": "Livro excluído com sucesso"}), 200

    except sqlite3.Error as e:
        return jsonify({'erro': f'Erro ao excluir livro: {e}'}), 500

if __name__ == "__main__":
    app.run(debug=True)
