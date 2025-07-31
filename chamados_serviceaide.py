from flask import Flask, render_template, request
import pyodbc

app = Flask(chamados_serviceaide)

# 🔐 Conexão com SQL Server
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.40.48.107,1433;"
    "DATABASE=CSMPROD;"
    "UID=usr_csm;"
    "PWD=DAdFw53BbZNqolTduOKj;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

@app.route('/', methods=['GET', 'POST'])
def index():
    dados_ticket = None
    logs = []
    tickets_encontrados = []
    ticket_id = None

    if request.method == 'POST':
        ticket_id = request.form.get('ticket')
        nome = request.form.get('nome')

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # 🔍 Se a busca for por nome (sem ticket)
        if nome and not ticket_id:
            sql_nome = """
                SELECT 
                    ticket_id,
                    CONCAT(person1_first_name, ' ', person1_last_name) AS nome,
                    CONVERT(VARCHAR, DATEADD(SECOND, created_date, '1970-01-01'), 103) AS data_abertura,
                    description_long
                FROM VAPP_INCIDENT
                WHERE CONCAT(person1_first_name, ' ', person1_last_name) LIKE '%' + ? + '%'

                UNION

                SELECT 
                    ticket_id,
                    CONCAT(person1_first_name, ' ', person1_last_name),
                    CONVERT(VARCHAR, DATEADD(SECOND, created_date, '1970-01-01'), 103),
                    description_long
                FROM VAPP_SERVICE_REQUEST
                WHERE CONCAT(person1_first_name, ' ', person1_last_name) LIKE '%' + ? + '%'
            """
            cursor.execute(sql_nome, nome, nome)
            tickets_encontrados = cursor.fetchall()

        # 🔍 Se a busca for por ticket (direta ou após escolher na lista)
        elif ticket_id:
            sql_ticket = """
                DECLARE @ticket_id INT = ?
                SELECT 
                    CONCAT(b.person1_first_name, ' ', b.person1_last_name) AS solicitante,
                    CONVERT(VARCHAR, DATEADD(SECOND, b.created_date, '1970-01-01'), 103) AS data_abertura,
                    b.description_long AS descricao,
                    CONCAT(a.case_id, ' ', a.ticket_id) AS Ticket,
                    a.work_description AS descricao_log,
                    CONVERT(VARCHAR, DATEADD(SECOND, a.work_created_date, '1970-01-01'), 103) AS data_log,
                    CONCAT(b.person1_first_name, ' ', b.person1_last_name) AS usuario_log
                FROM VAPP_WORK_LOG a
                JOIN VAPP_INCIDENT b ON a.ticket_id = b.ticket_id
                WHERE a.ticket_id = @ticket_id

                UNION ALL

                SELECT 
                    CONCAT(b.person1_first_name, ' ', b.person1_last_name),
                    CONVERT(VARCHAR, DATEADD(SECOND, b.created_date, '1970-01-01'), 103),
                    b.description_long,
                    CONCAT(a.case_id, ' ', a.ticket_id),
                    a.work_description,
                    CONVERT(VARCHAR, DATEADD(SECOND, a.work_created_date, '1970-01-01'), 103),
                    CONCAT(a.work_by_first_name, ' ', a.work_by_last_name)
                FROM VAPP_WORK_LOG a
                JOIN VAPP_SERVICE_REQUEST b ON a.ticket_id = b.ticket_id
                WHERE a.ticket_id = @ticket_id
            """
            cursor.execute(sql_ticket, ticket_id)
            results = cursor.fetchall()

            if results:
                dados_ticket = {
                    'solicitante': results[0][0],
                    'data_abertura': results[0][1],
                    'descricao': results[0][2]
                }
                for row in results:
                    logs.append({
                        'ticket': row[3],
                        'descricao_log': row[4],
                        'data_log': row[5],
                        'usuario_log': row[6]
                    })

        conn.close()

    return render_template('index.html', dados_ticket=dados_ticket, logs=logs, tickets_encontrados=tickets_encontrados)

if __name__ == '__main__':
    app.run(debug=True)
