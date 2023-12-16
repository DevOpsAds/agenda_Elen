import re
import os
import subprocess
import PySimpleGUI as sg
import csv
from datetime import datetime, timedelta


formato = '%H:%M'

def ler_agenda_md(caminho_arquivo):
    Tarefas = []
    with open(caminho_arquivo, 'r') as arquivo:
        Tarefa_atual = {}
        for linha in arquivo:
            # Verificando se a linha contém um título de Tarefa
            titulo_match = re.match(r'-\s*(.+)', linha)
            if titulo_match:
                if Tarefa_atual:
                    Tarefas.append(Tarefa_atual)
                Tarefa_atual = {'titulo': titulo_match.group(1).strip(), 'descricao': ''}
            
            # Verificando se a linha contém um horário
            horario_match = re.search(r'\*\*(\d{1,2}:\d{2}) - (\d{1,2}:\d{2})\*\*', linha)
            if horario_match:
                Tarefa_atual['inicio'] = horario_match.group(1)
                Tarefa_atual['fim'] = horario_match.group(2)

            # Capturando a descrição da Tarefa
            elif Tarefa_atual and not horario_match:
                Tarefa_atual['descricao'] += linha.strip() + ' '
    
    # Adicionando a última Tarefa lida
    if Tarefa_atual:
        Tarefas.append(Tarefa_atual)
    
    return Tarefas



#calcular projeção slite delimt
def calcular_horario_conclusao(horario_inicio, horario_progresso_atual, progresso_atual):
    formato = '%H:%M'
    inicio = datetime.strptime(horario_inicio, formato)
    progresso = datetime.strptime(horario_progresso_atual, formato)
    
    # Duração até o ponto de progresso atual
    duracao_ate_agora = progresso - inicio

    # Verifica se o progresso atual é 0 para evitar divisão por zero
    if progresso_atual == 0:
        return "Progresso atual é 0, cálculo impossível"

    # Calculando a duração total estimada com base no progresso atual
    duracao_total_estimada = duracao_ate_agora.total_seconds() / (progresso_atual / 100)

    # Calculando a hora de conclusão
    horario_conclusao = inicio + timedelta(seconds=duracao_total_estimada)
    return horario_conclusao.strftime(formato)


#processamento do csv
def consultar_request_agenda(nome_arquivo,agenda):
    controllInterface = []

    try:
        with open(nome_arquivo, mode='r') as arquivo_csv:
            leitor_csv = csv.reader(arquivo_csv)
            next(leitor_csv)  # Pula o cabeçalho
            for linha in leitor_csv:
                leitura = linha[0]
                Tarefa = linha[1]
                Descricao="mostra uma descriçao "
                Horario_inicial = Tarefa.split('-')[0].strip().split('**')[1]
                Horario_final = Tarefa.split('-')[1].strip().split('**')[0]
                mudar_DE_horario = datetime.strptime(linha[2], '%H:%M').time() if linha[2] else None
                s_Peso = float(linha[4])
                s_Progresso = float(linha[5])
                Horario_Alargar = calcular_horario_conclusao(Horario_inicial, leitura, s_Progresso)
                s_AJuSte = 100.0-float(linha[5])
                radio_continuar = linha[6] == 'True'
                check_concluida = linha[7] == 'True'
                check_confirmar_conclusao = linha[8] == 'True'
                check_abandonar_Tarefa = linha[9] == 'True'
                observacoes = linha[10]

                # Processamento dos dados
                # Exemplo de processamento
                inicio = datetime.strptime(Horario_inicial, formato)
                final_time_regitro = datetime.strptime(Horario_final, formato)
                leitura_register=datetime.strptime(leitura, formato)
                tempo_decorrido = ( leitura_register-inicio)
               
                
                ajuste_tempo = tempo_decorrido * s_AJuSte / s_Progresso if s_Progresso else 0

                # Códigos de escape ANSI para texto em vermelho
                ANSI_LARANJA = '\033[93m'
                ANSI_ROXO = '\033[95m'
                ANSI_RED = '\033[91m'
                ANSI_RESET = '\033[0m'



                print(f"Leitura: {leitura}, Tarefa: {Tarefa}, Mudar De Horário: {mudar_DE_horario},tempo_decorrido para: {ANSI_LARANJA}{tempo_decorrido},Alargar para: {ANSI_ROXO}{Horario_Alargar}{ANSI_RESET}, Ajuste Tempo: {ANSI_RED}{ajuste_tempo}{ANSI_RESET}, Peso: {s_Peso}, Progresso: {s_Progresso}, Continuar: {radio_continuar}, Concluída: {check_concluida}, Confirmar Conclusão: {check_confirmar_conclusao}, Abandonar Tarefa: {check_abandonar_Tarefa}, Observações: {observacoes}")
                controllInterface.append((Tarefa, Descricao, leitura, s_AJuSte, Horario_Alargar))  # Corrigido aqui
                return controllInterface

    except FileNotFoundError:
        print(f"Arquivo {nome_arquivo} não encontrado.")


        return []




def gravar_informacoes_csv(nome_arquivo, informacoes):
    # Definindo o cabeçalho
    cabecalho = ['Leirura','Tarefas', 'mudar_DE_horario', 's_AJuSte', 's_Peso', 
                 's_Progresso', 'Radio_cotinuar', 'check_Concluída', 
                 'Chec_Confirmar Conclusão', 'Check_Abandonar Tarefa', 'Input_Observações', 'Hora da Informação']

    # Verifica se o arquivo já existe
    arquivo_existe = os.path.exists(nome_arquivo)

    # Abre o arquivo para escrita
    with open(nome_arquivo, mode='a', newline='') as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # Se o arquivo não existe, escreve o cabeçalho
        if not arquivo_existe:
            escritor_csv.writerow(cabecalho)
        
        # Escreve as informações
        consultar_request_agenda(nome_arquivo)
        escritor_csv.writerow([datetime.now().strftime('%H:%M')] + informacoes)
       


#interface montagem
def interface_ajuste_Tarefa(Tarefa,Descricao,leitura,s_AJuSte, Horario_Alargar):
    print(Tarefa,Descricao,leitura,s_AJuSte, Horario_Alargar)
    layout = [
        [sg.Text(f"Leitura agora:{leitura}")],
        [sg.Text("Horário Estimado para Conclusão:"), sg.Text(Horario_Alargar)],
        [sg.Text("Título da Tarefa:"), sg.InputText(Tarefa)],
        [sg.Text("Ajuste a Tarefa"), sg.Text(Tarefa)],
        [sg.Text("Descrição da Tarefa:"), sg.Text(Descricao, size=(40, 3))],
        [sg.Text("Horário Previsto:"), sg.InputText(Horario_Alargar)],
        [sg.Text("Peso"), sg.Slider(range=(0, 20), orientation='h', size=(34, 20))],
        [sg.Text("Progresso"), sg.Slider(range=(0, 100), orientation='h', size=(34, 20))],
        [sg.Text("Slider de Ajuste de Horário"), sg.Slider(range=(s_AJuSte,100), orientation='h', size=(34, 20))],

        [sg.Radio("Continuar nesta Tarefa", "RADIO1"), sg.Radio("Prosseguir com a próxima", "RADIO1")],
        [sg.Checkbox("Concluída?"), sg.Checkbox("Confirmar conclusão?")],
        [sg.Checkbox("Abandonar essa Tarefa", text_color="red")],
        [sg.InputText("Observações")],
        [sg.Button("Informar")]
    ]
    window = sg.Window("Ajuste de Tarefa", layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Informar':
            # Extrai e imprime apenas os valores
            valores = list(values.values())
            print(', '.join(str(valor) for valor in valores))
            gravar_informacoes_csv(nome_arquivo,valores)
            break
    window.close()




def gerar_nome_arquivo_com_data(prefixo="agenda_"):
    data_atual = datetime.now().strftime("%Y%m%d")  # Formato: AAAAMMDD
    nome_arquivo = prefixo + data_atual + ".cv"   # Extensão .txt como exemplo
    return nome_arquivo

# Exemplo de uso



def init_agenda():  
    try:
        print("start - projeto 1")
        nome_arquivo = gerar_nome_arquivo_com_data()
        print(nome_arquivo)
        nome_arquivo = '/media/joao/Salmo5,13/pro/script.py/automacoes/openAi/'+nome_arquivo
        agenda = ler_agenda_md('/media/joao/Salmo5,13/pro/script.py/automacoes/openAi/Qi_json/Joao/elen/Agenda/Matrix_p/1_manha.md')
        

        Tarefas_conclusao = consultar_request_agenda(nome_arquivo,agenda)
        print(Tarefas_conclusao)


        if Tarefas_conclusao is None or not Tarefas_conclusao:
            for Tarefa,Descricao,leitura,s_AJuSte, Horario_Alargar in Tarefas_conclusao:
                interface_ajuste_Tarefa(Tarefa,Descricao,leitura,s_AJuSte, Horario_Alargar)
        else:
            caminho_script = '/media/joao/Salmo5,13/pro/script.py/automacoes/openAi/Qi_json/Joao/format_project copy 2/1_pach_main.py'
            # Executando o script como um subprocesso

                # Nome do arquivo para passar como argumento


            # Executando o script como um subprocesso com um argumento
            subprocess.Popen(['python', caminho_script, nome_arquivo])

            subprocess.Popen(['python', caminho_script])



    except FileNotFoundError:
    
        
        print(f"Arquivo {nome_arquivo} não encontrado.")

init_agenda()