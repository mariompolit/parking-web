from flask import Flask, request, render_template_string
import requests, datetime, math

# Configuración
API_KEY = 'TU_API_KEY'
ENTRY_FORM_ID = 'ID_FORM_INGRESO'

ingreso_qids = {'idUnico': '3', 'placa': '4'}

app = Flask(__name__)

def buscar_ingreso(ticket):
    url = f'https://api.jotform.com/form/{ENTRY_FORM_ID}/submissions'
    params = {'apiKey': API_KEY, 'limit': 1000}
    r = requests.get(url, params=params)
    r.raise_for_status()
    submissions = r.json()['content']
    qid_ticket = ingreso_qids['idUnico']
    for sub in submissions:
        if sub['answers'][qid_ticket]['answer'] == ticket:
            return sub
    return None

def calcular_total(submission):
    created = submission['created_at']
    entry_dt = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
    exit_dt = datetime.datetime.now()
    seconds = (exit_dt - entry_dt).total_seconds()
    horas = math.ceil(seconds / 3600)
    return horas * 1.5

# Plantilla HTML mínima
FORM_HTML = """
<h2>Salida de Vehículo</h2>
<form method="post">
    <label for="ticket">Número de ticket:</label>
    <input type="text" name="ticket" id="ticket" required>
    <button type="submit">Calcular</button>
</form>
{% if total is not none %}
    {% if encontrado %}
        <p>Placa: {{ placa }}</p>
        <p>Total a pagar: ${{ total }}</p>
    {% else %}
        <p style="color:red;">Ticket no encontrado.</p>
    {% endif %}
{% endif %}
"""

@app.route('/', methods=['GET', 'POST'])
def salida():
    total = None
    placa = ''
    encontrado = False
    if request.method == 'POST':
        ticket = request.form['ticket'].strip()
        submission = buscar_ingreso(ticket)
        if submission:
            encontrado = True
            placa = submission['answers'][ingreso_qids['placa']]['answer']
            total = calcular_total(submission)
        else:
            encontrado = False
    return render_template_string(FORM_HTML, total=total, placa=placa, encontrado=encontrado)

if __name__ == '__main__':
    app.run(debug=True)
