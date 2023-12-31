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
def consultar_request_agenda(nome_arquivo):
    leitor_csv = csv.DictReader(nome_arquivo)
    controllInterface = []

    try:

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
                controllInterface.append((Tarefa, Descricao,mudar_DE_horario, leitura, s_AJuSte, Horario_Alargar))  # Corrigido aqui
                return controllInterface

    except FileNotFoundError:
        print(f"Arquivo não encontrado.")


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
def interface_ajuste_Tarefa(nome_arquivo,Tarefa,Descricao,leitura,s_AJuSte, Horario_Alargar):
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
    nome_arquivo = prefixo + data_atual + ".csv"   # Extensão .txt como exemplo
    return nome_arquivo



def verificar_existencia_arquivo(caminho):
    """
    Verifica se um arquivo existe no caminho especificado.

    :param caminho: str, o caminho do arquivo a ser verificado.
    :return: bool, True se o arquivo existir, False caso contrário.
    """
    return os.path.isfile(caminho)


def atualizar_registro_concluido(caminho_arquivo, tarefa_atual):
    registros = []
    registro_atualizado = False
    with open(caminho_arquivo, 'r') as arquivo_csv:
        leitor_csv = csv.DictReader(arquivo_csv)
        for linha in leitor_csv:
            if linha['Tarefas'] == tarefa_atual and linha['check_Concluída'] == 'False' and not registro_atualizado:
                linha['check_Concluída'] = 'True'
                registro_atualizado = True
            registros.append(linha)

    with open(caminho_arquivo, 'w', newline='') as arquivo_csv:
        escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=leitor_csv.fieldnames)
        escritor_csv.writeheader()
        escritor_csv.writerows(registros)

def adicionar_novo_registro(caminho_arquivo, novos_valores):
    horario_atual = datetime.now().strftime("%H:%M")
    novos_valores_atualizados = {'Leirura': horario_atual, **novos_valores}

    with open(caminho_arquivo, 'a', newline='') as arquivo_csv:
        escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=novos_valores_atualizados.keys())
        escritor_csv.writerow(novos_valores_atualizados)




def wwadicionar_novo_registro(caminho_arquivo, novos_valores):
    # Obtém o horário atual no formato HH:MM
    horario_atual = datetime.now().strftime("%H:%M")

    # Atualiza o dicionário de novos valores, adicionando o horário atual na primeira coluna
    novos_valores_atualizados = {'Leirura': horario_atual, **novos_valores}

    with open(caminho_arquivo, 'a', newline='') as arquivo_csv:
        escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=novos_valores_atualizados.keys())
        escritor_csv.writerow(novos_valores_atualizados)

# Uso da função adicionar_novo_registro
# Suponha que 'novos_valores' seja um dicionário com os valores coletados da interface
# Por exemplo: novos_valores = {'Tarefas': 'Nova Tarefa', 'Mudar_de_horario': '17:00', ...}


def analisar_arquivo_csv(caminho_arquivo):
    agora = datetime.now().time()  # Obtém o horário atual
    formato_horario = '%H:%M'

    with open(caminho_arquivo, mode='r') as arquivo_csv:
        leitor_csv = csv.DictReader(arquivo_csv)
        for linha in leitor_csv:
            horario_mudar = datetime.strptime(linha['Mudar_de_horario'], formato_horario).time()
            horario_acordado =linha['Tarefas'].split('**')[1].strip()  # Extraindo o horário acordado
                        
            check_confirmar_conclusao= linha['Chec_Confirmar_Conclusão'] == 'True'
            check_concluida = linha['check_Concluída'] == 'True'
            check_abandonar = linha['Check_Abandonar_Tarefa'] == 'True'
            leitura = linha['Leirura']
            Tarefa = linha['Tarefas']
            Descricao="mostra uma descriçao "
            Horario_inicial = Tarefa.split('-')[0].strip().split('**')[1]
            Horario_final = Tarefa.split('-')[1].strip().split('**')[0]
            s_Peso = float(linha['S_peso'])
            s_Progresso = float(linha['S_progresso'])

            Horario_Alargar = calcular_horario_conclusao(Horario_inicial, leitura, s_Progresso)
            s_AJuSte = 100.0-float(linha['S_progresso'])
            radio_continuar = linha['Radio_cotinuar'] == 'True'
            observacoes = linha['Input_Observações']

                # Processamento dos dados
                # Exemplo de processamento
            inicio = datetime.strptime(Horario_inicial, formato)
            final_time_regitro = datetime.strptime(Horario_final, formato)
            leitura_register=datetime.strptime(leitura, formato)
            tempo_decorrido = ( leitura_register-inicio)
               
                
            ajuste_tempo = tempo_decorrido * s_AJuSte / s_Progresso if s_Progresso else 0
            if horario_mudar != horario_acordado and not (check_concluida or check_abandonar) and horario_mudar < agora:
                print("Vistoriar")


                # Códigos de escape ANSI para texto em vermelho
                ANSI_LARANJA = '\033[93m'
                ANSI_ROXO = '\033[95m'
                ANSI_RED = '\033[91m'
                ANSI_RESET = '\033[0m'



                print(f"Leitura: {leitura}, Tarefa: {Tarefa}, Mudar De Horário: {horario_mudar},tempo_decorrido para: {ANSI_LARANJA}{tempo_decorrido},Alargar para: {ANSI_ROXO}{Horario_Alargar}{ANSI_RESET}, Ajuste Tempo: {ANSI_RED}{ajuste_tempo}{ANSI_RESET}, Peso: {s_Peso}, Progresso: {s_Progresso}, Continuar: {radio_continuar}, Concluída: {check_concluida}, Confirmar Conclusão: {check_confirmar_conclusao}, Abandonar Tarefa: {check_abandonar}, Observações: {observacoes}")


                # Supondo que as funções atualizar_registro_concluido, adicionar_novo_registro e gravar_informacoes_csv já estão definidas



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
                    [sg.Checkbox("Concluída?", key="concluida"), sg.Checkbox("Confirmar conclusão?")],
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
                    # Se a tarefa estiver concluída, atualiza o registro existente
                        if values["concluida"]:
                            atualizar_registro_concluido(caminho_arquivo, Tarefa)
                        else:
                            # Cria um novo registro com os valores da interface
                            novos_valores = {key: value for key, value in values.items()}
                            adicionar_novo_registro(caminho_arquivo, novos_valores)

                        # Extrai e imprime apenas os valores
                        valores = list(values.values())
                        print(', '.join(str(valor) for valor in valores))
                        gravar_informacoes_csv(caminho_arquivo, valores)
                        break
                window.close()



        menor_tempo_restante = None
        tarefa_com_menor_tempo = None

        with open(caminho_arquivo, mode='r') as arquivo:
            leitor_csv = csv.DictReader(arquivo)
            for linha in leitor_csv:
                horario_mudar = datetime.strptime(linha['Mudar_de_horario'], formato_horario).time()
                check_concluida = linha['check_Concluída'] == 'True'
                check_abandonar = linha['Check_Abandonar_Tarefa'] == 'True'

                if not (check_concluida or check_abandonar):
                    agora = datetime.now()
                    horario_mudar_full = datetime.combine(agora.date(), horario_mudar)
                    tempo_restante = horario_mudar_full - agora
                    if menor_tempo_restante is None or tempo_restante < menor_tempo_restante:
                        menor_tempo_restante = tempo_restante
                        tarefa_com_menor_tempo = linha['Tarefas']

        # Se encontrou uma tarefa, fazer algo com ela
        if tarefa_com_menor_tempo:
            print(f"A tarefa com menor tempo restante é: {tarefa_com_menor_tempo}, tempo restante: {menor_tempo_restante}")
            if tarefa_com_menor_tempo and menor_tempo_restante:
                tempo_restante_segundos = int(menor_tempo_restante.total_seconds())
                contadorCamnho='/media/joao/Salmo5,13/pro/script.py/automacoes/openAi/Qi_json/Joao/format_project copy 3/contador_regressivo.py'
                subprocess.Popen(["python",contadorCamnho, str(tempo_restante_segundos)])
            else:
                print("Não há tarefas pendentes com mudança de horário iminente.")
        else:
            print("Não há tarefas pendentes com mudança de horário iminente.")





def init_agenda():  
    try:
        #cria um nome sugestivo para aquivo agenda 
        print("start - projeto 1")
        nome_arquivo = gerar_nome_arquivo_com_data()
        print(nome_arquivo)
        nome_arquivo = '/media/joao/Salmo5,13/pro/script.py/automacoes/openAi/Qi_json/Joao/elen/Agenda/concluidas'+nome_arquivo
        
        #verifica se existe o aquivo 
        existe = verificar_existencia_arquivo(nome_arquivo)
        print(f"O arquivo existe: {existe}")
        agenda = ler_agenda_md('/media/joao/Salmo5,13/pro/script.py/automacoes/openAi/Qi_json/Joao/elen/Agenda/Matrix_p/1_manha.md')
        if (existe):
            print("conexão com ptyhon OK")
            analisar_arquivo_csv(nome_arquivo)


        else:
            caminho_script='/media/joao/Salmo5,13/pro/script.py/automacoes/openAi/Qi_json/Joao/format_project copy 2/1_pach_main.py'
            print("Abrindo estudo de agenda ")
        
            # Executando o script como um subprocesso com um argumento
            subprocess.Popen(['python', caminho_script, nome_arquivo])

    
        



    except FileNotFoundError:
    
        
        print(f"Arquivo {nome_arquivo} não encontrado.")

init_agenda()