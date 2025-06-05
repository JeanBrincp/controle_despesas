from flask import Flask, render_template, request, redirect, url_for, jsonify
import pyodbc
from decimal import Decimal, InvalidOperation
from datetime import datetime

app = Flask(__name__)

# Configuração da conexão com SQL Server
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=172.20.0.33,1433;'
        'DATABASE=despesas_db;'
        'UID=jean_user;'
        'PWD=123456;'
    )
    return conn

@app.route('/')
def index():
    return redirect(url_for('lancamento'))

# Página de lançamento de despesas
@app.route('/lancamento', methods=['GET', 'POST'])
def lancamento():
    sucesso = request.args.get('sucesso')
    erro = request.args.get('erro')

    if request.method == 'POST':
        try:
            numero_empenho = request.form.get('numero_empenho', '').strip()
            secretaria = request.form.get('secretaria', '').strip()
            tipo_despesa = request.form.get('tipo_despesa', '').strip()
            credor = request.form.get('credor', '').strip()
            elemento = request.form.get('elemento', '').strip()
            acao = request.form.get('acao', '').strip()
            data_str = request.form.get('data', '').strip()  # Expecting 'YYYY-MM-DD' format
            mes = request.form.get('mes', '').strip()  # formato MM/YYYY
            valor_empenhado = request.form.get('valor_empenhado', '0').replace(',', '.').strip()
            valor_empenhado_pagar = request.form.get('valor_empenhado_pagar', '0').replace(',', '.').strip()
            valor_liquidado = request.form.get('valor_liquidado', '0').replace(',', '.').strip()
            valor_a_liquidar = request.form.get('valor_a_liquidar', '0').replace(',', '.').strip()
            valor_liquidado_pagar = request.form.get('valor_liquidado_pagar', '0').replace(',', '.').strip()
            valor_baixado = request.form.get('valor_baixado', '0').replace(',', '.').strip()
            valor_pago = request.form.get('valor_pago', '0').replace(',', '.').strip()

            # Converter data
            data = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else None

            # Converter valores para Decimal
            def to_decimal(v):
                try:
                    return Decimal(v)
                except InvalidOperation:
                    return Decimal('0.00')

            valor_empenhado = to_decimal(valor_empenhado)
            valor_empenhado_pagar = to_decimal(valor_empenhado_pagar)
            valor_liquidado = to_decimal(valor_liquidado)
            valor_a_liquidar = to_decimal(valor_a_liquidar)
            valor_liquidado_pagar = to_decimal(valor_liquidado_pagar)
            valor_baixado = to_decimal(valor_baixado)
            valor_pago = to_decimal(valor_pago)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO despesas (
                    numero_empenho, secretaria, tipo_despesa, credor, elemento, acao, data, mes,
                    valor_empenhado, valor_empenhado_pagar, valor_liquidado, valor_a_liquidar,
                    valor_liquidado_pagar, valor_baixado, valor_pago
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                numero_empenho, secretaria, tipo_despesa, credor, elemento, acao, data, mes,
                valor_empenhado, valor_empenhado_pagar, valor_liquidado, valor_a_liquidar,
                valor_liquidado_pagar, valor_baixado, valor_pago
            ))
            conn.commit()
            conn.close()

            return redirect(url_for('lancamento', sucesso='Despesa lançada com sucesso!'))
        except Exception as e:
            print(f"Erro: {e}")
            return redirect(url_for('lancamento', erro='Erro ao lançar despesa.'))

    # Mesmas listas para dropdown (pode ajustar conforme precisar)
    secretarias = [
        "GABINETE E SECRETARIA DO PREFEITO",
        "SECRETARIA DE PLANEJAMENTO",
        "GOVERNO E COMUNICACAO SOCIAL",
        "SECRETARIA DE DESENVOLVIMENTO SOCIAL",
        "INDUSTRIA, COMERCIO E DESENVOLVIMENTO ECONOMICO",
        "ESPORTE, CULTURA E LAZER",
        "PROCURADORIA GERAL",
        "SECRETARIA DE ADMINISTRACAO",
        "SECRETARIA DE EDUCACAO",
        "SECRETARIA DE FAZENDA",
        "SECRETARIA DE OBRAS E URBANISMO",
        "SECRETARIA DE MEIO AMBIENTE E SERVICOS URBANOS",
        "CONTROLADORIA GERAL DO MUNICIPIO"
    ]

    tipos_despesa = [
        "Pessoal e Encargos Sociais",
        "Outras Despesas Correntes",
        "Investimentos",
        "Juros e Encargos da Dívida",
        "Amortização da Dívida"
    ]

    credores = [
        "PREFEITURA MUNICIPAL DE IBIRITE",
        "INSS-INSTITUTO NACIONAL DE SEGURIDADE SO",
        "VIVA CONSULTORIA ESTRATEGICA LTDA"
    ]

    elementos = [
        "3.1.90.11.00 - Vencimentos e Vantagens Fixas - Pessoal Civil",
        "3.1.90.13.00 - Obrigações Patronais"
    ]

    return render_template(
        'lancamento.html',
        secretarias=secretarias,
        tipos_despesa=tipos_despesa,
        credores=credores,
        elementos=elementos,
        sucesso=sucesso,
        erro=erro
    )


# -------------------------------
# Endpoints GET
# -------------------------------

@app.route('/api/secretarias', methods=['GET'])
def get_secretarias():
    return jsonify(secretarias), 200

@app.route('/api/tipos_despesa', methods=['GET'])
def get_tipos_despesa():
    return jsonify(tipos_despesa), 200

@app.route('/api/credores', methods=['GET'])
def get_credores():
    return jsonify(credores), 200

@app.route('/api/elementos', methods=['GET'])
def get_elementos():
    return jsonify(elementos), 200

@app.route('/api/listas', methods=['GET'])
def get_todas_listas():
    """Endpoint opcional para pegar tudo de uma vez"""
    return jsonify({
        "secretarias": secretarias,
        "tipos_despesa": tipos_despesa,
        "credores": credores,
        "elementos": elementos
    }), 200

# -------------------------------
# Endpoints POST
# -------------------------------

@app.route('/api/credores', methods=['POST'])
def add_credor():
    data = request.get_json()
    novo_credor = data.get('nome')
    
    if not novo_credor:
        return jsonify({"error": "Nome do credor é obrigatório"}), 400
    if novo_credor in credores:
        return jsonify({"error": "Credor já existe"}), 400

    credores.append(novo_credor)
    return jsonify({"message": "Credor adicionado com sucesso", "credor": novo_credor}), 201

@app.route('/api/elementos', methods=['POST'])
def add_elemento():
    data = request.get_json()
    novo_elemento = data.get('nome')
    
    if not novo_elemento:
        return jsonify({"error": "Nome do elemento é obrigatório"}), 400
    if novo_elemento in elementos:
        return jsonify({"error": "Elemento já existe"}), 400

    elementos.append(novo_elemento)
    return jsonify({"message": "Elemento adicionado com sucesso", "elemento": novo_elemento}), 201

# -------------------------------
# Main
# -------------------------------




# Página para visualizar despesas com busca
@app.route('/despesas')
def despesas():
    busca = request.args.get('busca', '').strip()
    sucesso = request.args.get('sucesso')
    erro = request.args.get('erro')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if busca:
            sql = """
            SELECT id, numero_empenho, secretaria, tipo_despesa, credor, elemento, acao, data, mes,
                   valor_empenhado, valor_empenhado_pagar, valor_liquidado, valor_a_liquidar,
                   valor_liquidado_pagar, valor_baixado, valor_pago
            FROM despesas
            WHERE credor LIKE ? OR secretaria LIKE ?
            """
            cursor.execute(sql, ('%' + busca + '%', '%' + busca + '%'))
        else:
            sql = """
            SELECT id, numero_empenho, secretaria, tipo_despesa, credor, elemento, acao, data, mes,
                   valor_empenhado, valor_empenhado_pagar, valor_liquidado, valor_a_liquidar,
                   valor_liquidado_pagar, valor_baixado, valor_pago
            FROM despesas
            """
            cursor.execute(sql)

        despesas = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")
        erro = str(e)
        despesas = []

    # Converter os resultados para um formato mais amigável
    return render_template(
        'despesas.html',
        despesas=despesas,
        busca=busca,
        sucesso=sucesso,
        erro=erro
    )

# Rota para excluir uma despesa
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM despesas WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('despesas', sucesso='Despesa excluída com sucesso!'))
    except Exception as e:
        print(f"Erro: {e}")
        return redirect(url_for('despesas', erro='Erro ao excluir a despesa.'))

# Rota para editar uma despesa
@app.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    try:
        numero_empenho = request.form.get('numero_empenho', '').strip()
        secretaria = request.form.get('secretaria', '').strip()
        tipo_despesa = request.form.get('tipo_despesa', '').strip()
        credor = request.form.get('credor', '').strip()
        elemento = request.form.get('elemento', '').strip()
        acao = request.form.get('acao', '').strip()
        data_str = request.form.get('data', '').strip()
        mes = request.form.get('mes', '').strip()
        valor_empenhado = request.form.get('valor_empenhado', '0').replace(',', '.').strip()
        valor_empenhado_pagar = request.form.get('valor_empenhado_pagar', '0').replace(',', '.').strip()
        valor_liquidado = request.form.get('valor_liquidado', '0').replace(',', '.').strip()
        valor_a_liquidar = request.form.get('valor_a_liquidar', '0').replace(',', '.').strip()
        valor_liquidado_pagar = request.form.get('valor_liquidado_pagar', '0').replace(',', '.').strip()
        valor_baixado = request.form.get('valor_baixado', '0').replace(',', '.').strip()
        valor_pago = request.form.get('valor_pago', '0').replace(',', '.').strip()

        data = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else None

        def to_decimal(v):
            try:
                return Decimal(v)
            except InvalidOperation:
                return Decimal('0.00')

        valor_empenhado = to_decimal(valor_empenhado)
        valor_empenhado_pagar = to_decimal(valor_empenhado_pagar)
        valor_liquidado = to_decimal(valor_liquidado)
        valor_a_liquidar = to_decimal(valor_a_liquidar)
        valor_liquidado_pagar = to_decimal(valor_liquidado_pagar)
        valor_baixado = to_decimal(valor_baixado)
        valor_pago = to_decimal(valor_pago)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE despesas SET
                numero_empenho = ?,
                secretaria = ?,
                tipo_despesa = ?,
                credor = ?,
                elemento = ?,
                acao = ?,
                data = ?,
                mes = ?,
                valor_empenhado = ?,
                valor_empenhado_pagar = ?,
                valor_liquidado = ?,
                valor_a_liquidar = ?,
                valor_liquidado_pagar = ?,
                valor_baixado = ?,
                valor_pago = ?
            WHERE id = ?
        ''', (
            numero_empenho, secretaria, tipo_despesa, credor, elemento, acao, data, mes,
            valor_empenhado, valor_empenhado_pagar, valor_liquidado, valor_a_liquidar,
            valor_liquidado_pagar, valor_baixado, valor_pago, id
        ))
        conn.commit()
        conn.close()

        return redirect(url_for('despesas', sucesso='Despesa editada com sucesso!'))
    except Exception as e:
        print(f"Erro: {e}")
        return redirect(url_for('despesas', erro='Erro ao editar a despesa.'))
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
