# Importando biblioteca
from tkinter import *
import re
import math

# Cores
cor1 = "#B9B9B9" # Cinza
cor2 = "#5f5e5e" # Cinza escuro
cor4 = "#00BFFF" # Deep sky blue

# --- Parâmetros de Configuração da Calculadora ---
LARGURA_JANELA = 300
ALTURA_JANELA = 380

ALTURA_TELA_PX = int(ALTURA_JANELA * 0.25)
ALTURA_CORPO_PX = ALTURA_JANELA - ALTURA_TELA_PX

NUM_COLUNAS = 4
NUM_LINHAS_CORPO = 6

LARGURA_CELULA_PX = LARGURA_JANELA / NUM_COLUNAS
ALTURA_CELULA_PX = ALTURA_CORPO_PX / NUM_LINHAS_CORPO

TAMANHO_FONTE_BOTOES = 16
TAMANHO_FONTE_TELA = 24
TAMANHO_FONTE_HISTORICO = 12 # Novo tamanho para a fonte do histórico

FONTE_OPERADORES = ('Arial', TAMANHO_FONTE_BOTOES, 'bold')
FONTE_NUMEROS = ('Arial', TAMANHO_FONTE_BOTOES)
FONTE_IGUAL = ('Arial', TAMANHO_FONTE_BOTOES, 'bold')
FONTE_HISTORICO = ('Arial', TAMANHO_FONTE_HISTORICO) # Nova fonte para o histórico

# Criação da janela
janela = Tk()
janela.title("Calculadora")
janela.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}")
janela.resizable(False, False)

# Dividindo a janela
frameTela = Frame(janela, width=LARGURA_JANELA, height=ALTURA_TELA_PX)
frameTela.grid(row=0, column=0)

frameCorpo = Frame(janela, width=LARGURA_JANELA, height=ALTURA_CORPO_PX, bg=cor1)
frameCorpo.grid(row=1, column=0)

# Variável que armazena todos os valores
todos_valores = ""
historico_operacao = "" # Nova variável para o histórico da operação
resultado_anterior = "" # Nova variável para o resultado anterior

# Funções
def entrar_valores(event):
    global todos_valores
    global historico_operacao
    global resultado_anterior
    
    # Botão de limpar tela
    if event == 'C':
        limpar_tela()

    # Botão de igualdade 
    elif event == '=':
        calcular()
    # Troca de Sinal
    elif event == '+/-':
        match = re.search(r'(-?\d+\.?\d*)$', todos_valores)
        if match:
            numero = match.group(1)
            numero_invertido = numero[1:] if numero.startswith('-') else '-' + numero
            todos_valores = todos_valores[:match.start()] + numero_invertido
        elif not todos_valores:
            todos_valores = '-'
        valor_texto.set(todos_valores)
        ajustar_scroll_entry() # Ajusta o scroll após a mudança de sinal
        
    # Cálculo da porcentagem 
    elif event == '%':
        # Permite '%' apenas se houver um número ou ')' anterior
        if todos_valores and (todos_valores[-1].isdigit() or todos_valores[-1] == ')'):
            todos_valores += '%'
        else:
            valor_texto.set("Inválido!") # Mensagem de erro para % inválido
            todos_valores = "" # Limpa a entrada após o erro
        ajustar_scroll_entry() # Ajusta o scroll após adicionar %

    # Cálculo da raiz
    elif event == '√':
        # Se a entrada está vazia ou termina com operador/parêntese abrindo, adiciona '√('
        if not todos_valores or todos_valores[-1] in ['+', '-', '*', '/', 'x', '÷', '(']:
            todos_valores += '√('
        # Se termina com um número, insere '√(' antes do número
        elif todos_valores[-1].isdigit():
            match = re.search(r'(\d+\.?\d*)$', todos_valores)
            if match:
                start_index = match.start()
                num_to_sqrt = match.group(1)
                todos_valores = todos_valores[:start_index] + '√(' + num_to_sqrt + ')'
            else: # Caso raro onde isdigit é True mas regex não encontra número (ex: após erro)
                todos_valores += '√('
        else: # Se termina com um operador, mas não um parêntese abrindo
            todos_valores += '√('
        ajustar_scroll_entry() # Ajusta o scroll após adicionar raiz

    # Adição da vírgula, ou seja, float
    elif event == '.':
        parts = re.split(r'[\+\-\*\/√()]', todos_valores) 
        if parts and '.' in parts[-1]:
            pass
        else:
            todos_valores += str(event)
        ajustar_scroll_entry() # Ajusta o scroll após adicionar vírgula

    # Abre e fecha parênteses
    elif event == '(': 
        todos_valores += '('
        ajustar_scroll_entry() # Ajusta o scroll
    elif event == ')': 
        todos_valores += ')'
        ajustar_scroll_entry() # Ajusta o scroll
    else: 
        # Se for um número ou operador, limpa o histórico se um resultado foi exibido
        if resultado_anterior and event not in ['+', '-', '*', '/', 'x', '÷', '%', '√', '.', '(', ')']:
            todos_valores = "" # Reseta a entrada atual se um novo número for digitado após um resultado
            historico_operacao = ""
            resultado_anterior = ""
            historico_texto.set(historico_operacao)
        elif resultado_anterior and event in ['+', '-', '*', '/', 'x', '÷']:
            todos_valores = resultado_anterior + str(event) # Continua com o resultado anterior
            historico_operacao = ""
            resultado_anterior = ""
            historico_texto.set(historico_operacao)
        else:
            pass # Continua adicionando à expressão atual

        todos_valores += str(event)
        ajustar_scroll_entry() # Ajusta o scroll após adicionar o caractere

    valor_texto.set(todos_valores)
    # Atualiza o histórico se não houver um cálculo pendente e não for uma limpeza
    if event != '=' and event != 'C':
        historico_texto.set(historico_operacao)


# Função para calcular os valores
def calcular():
    global todos_valores
    global historico_operacao # Usar a variável global de histórico
    global resultado_anterior

    try:
        expressao_original = todos_valores # Guarda a expressão antes de ser modificada para cálculo
        expressao_final = todos_valores.replace('÷', '/').replace('x', '*')

        # 1. Resolver Raízes Quadradas
        # Primeiro, trata raízes com parênteses, ex: "√(9)"
        expressao_final = re.sub(r'√\(([^)]*)\)', r'math.sqrt(\1)', expressao_final)
        # Depois, trata raízes diretas de números, ex: "√9"
        expressao_final = re.sub(r'√(\d+\.?\d*)', r'math.sqrt(\1)', expressao_final)


        # 2. Resolver Porcentagens
        while '%' in expressao_final:
            match_percent = re.search(r'(\d+\.?\d*)%', expressao_final)
            if not match_percent:
                # Se não encontrar mais padrões de porcentagem, sai do loop
                break

            percent_num_str = match_percent.group(1)
            percent_value = float(percent_num_str)
            
            percent_start_idx = match_percent.start()
            percent_end_idx = match_percent.end()

            pre_percent_segment = expressao_final[:percent_start_idx]

            base_operator_match = re.search(
                r'((?:\d+\.?\d*|\([^)]*\)))\s*([\+\-\*\/])\s*$', 
                pre_percent_segment
            )
            
            calculated_segment = None

            if base_operator_match:
                base_expr_str = base_operator_match.group(1)
                op_char = base_operator_match.group(2)
                
                try:
                    base_value = eval(base_expr_str.strip(), {"math": math})
                    
                    if op_char == '+':
                        calculated_segment = str(base_value + (base_value * (percent_value / 100)))
                    elif op_char == '-':
                        calculated_segment = str(base_value - (base_value * (percent_value / 100)))
                    elif op_char == '*':
                        calculated_segment = str(base_value * (percent_value / 100))
                    elif op_char == '/':
                        if percent_value == 0:
                            raise ZeroDivisionError("Divisão por zero com porcentagem zero.")
                        calculated_segment = str(base_value / (percent_value / 100))
                    
                    base_start_in_full_expr = pre_percent_segment.rfind(base_expr_str.strip())
                    
                    expressao_final = (expressao_final[:base_start_in_full_expr] + 
                                       calculated_segment + 
                                       expressao_final[percent_end_idx:]) 
                except Exception:
                    # Se houver um erro na avaliação da base, trata a porcentagem como divisão por 100
                    calculated_segment = str(percent_value / 100)
                    expressao_final = (expressao_final[:percent_start_idx] + 
                                       calculated_segment + 
                                       expressao_final[percent_end_idx:])
            else:
                # Se não houver operador antes da porcentagem, trata como valor / 100
                calculated_segment = str(percent_value / 100)
                expressao_final = (expressao_final[:percent_start_idx] + 
                                   calculated_segment + 
                                   expressao_final[percent_end_idx:])
        
        # 3. Avaliar a expressão final com math no contexto
        resultado = str(eval(expressao_final, {"math": math}))
        
        if resultado.endswith('.0'):
            resultado = resultado[:-2]

        historico_operacao = expressao_original + " =" # Guarda a expressão original
        historico_texto.set(historico_operacao) # Atualiza o label do histórico
        valor_texto.set(resultado)
        todos_valores = resultado
        resultado_anterior = resultado # Armazena o resultado para uso posterior
        ajustar_scroll_entry() # Ajusta o scroll para mostrar o final do resultado
    except ZeroDivisionError:
        valor_texto.set("Erro: Div por zero")
        todos_valores = ""
        historico_operacao = "" 
        historico_texto.set(historico_operacao)
        resultado_anterior = ""
        ajustar_scroll_entry()
    except ValueError as e: # Captura erros de domínio matemático, como sqrt de negativo
        if "math domain error" in str(e):
            valor_texto.set("Erro: Raiz de negativo")
        else:
            valor_texto.set("Erro de valor")
        todos_valores = ""
        historico_operacao = "" 
        historico_texto.set(historico_operacao)
        resultado_anterior = ""
        ajustar_scroll_entry()
    except SyntaxError: # Captura erros de sintaxe na expressão
        valor_texto.set("Erro: Sintaxe inválida")
        todos_valores = ""
        historico_operacao = "" 
        historico_texto.set(historico_operacao)
        resultado_anterior = ""
        ajustar_scroll_entry()
    except TypeError: # Captura erros de tipo
        valor_texto.set("Erro: Tipo inválido")
        todos_valores = ""
        historico_operacao = "" 
        historico_texto.set(historico_operacao)
        resultado_anterior = ""
        ajustar_scroll_entry()
    except Exception as e: # Captura qualquer outro erro inesperado
        valor_texto.set("Erro")
        todos_valores = ""
        historico_operacao = "" 
        historico_texto.set(historico_operacao)
        resultado_anterior = ""
        ajustar_scroll_entry()


# Função de limpar tela 
def limpar_tela():
    global todos_valores
    global historico_operacao
    global resultado_anterior
    todos_valores = ""
    historico_operacao = ""
    resultado_anterior = ""
    valor_texto.set("")
    historico_texto.set("") # Limpa o histórico também
    ajustar_scroll_entry() # Ajusta o scroll ao limpar a tela

# Função de apagar apenas os últimos dígitos
def backspace():
    global todos_valores
    global historico_operacao
    global resultado_anterior
    todos_valores = todos_valores[:-1]
    valor_texto.set(todos_valores)
    historico_texto.set(historico_operacao) # Mantém o histórico como está
    ajustar_scroll_entry() # Ajusta o scroll ao apagar

# Função para ajustar o scroll do Entry
def ajustar_scroll_entry():
    # Isso fará com que o Entry "scrolle" para a direita, mostrando o final do texto
    app_entry.xview_moveto(1.0) # Move o scrollbar para o final

# Label para exibir o histórico
historico_texto = StringVar()
historico_label = Label(
    frameTela,
    textvariable=historico_texto,
    padx=7,
    relief=FLAT,
    anchor="e",
    justify=RIGHT,
    fg="#888888", # Cor mais suave para o histórico
    font=FONTE_HISTORICO
)
historico_label.place(
    relx=0,
    rely=0, # Começa no topo
    relwidth=1,
    relheight=0.3 # Ocupa a parte superior da tela
)

# Campo de entrada/visualização principal (agora um Entry)
valor_texto = StringVar()
app_entry = Entry( # Alterado de Label para Entry
    frameTela,
    textvariable=valor_texto,
    width=20, # Largura padrão do Entry, pode ser ajustada
    state='readonly', # Impede a digitação direta pelo teclado
    readonlybackground="white", # Fundo branco quando readonly
    highlightthickness=0, # Remove borda padrão
    bd=0, # Remove borda 3D
    relief=FLAT, # Remove relevo
    justify=RIGHT, # Alinha o texto à direita
    font=('Arial',
    TAMANHO_FONTE_TELA, 'bold')
)
app_entry.place(
    relx=0,
    rely=0.3, # Ajusta a posição para dar espaço ao histórico
    relwidth=1,
    relheight=0.7 # Reduz a altura para dar espaço ao histórico
)

# Linkar o Entry com a função de ajuste de scroll para garantir que o final sempre apareça
# Isso é importante para o comportamento de "dízima evoluindo da esquerda para a direita"
valor_texto.trace_add("write", lambda name, index, mode: ajustar_scroll_entry())

# --- Funções auxiliares para posicionamento ---
def get_x_pos(col):
    return col * LARGURA_CELULA_PX

def get_y_pos(row):
    return row * ALTURA_CELULA_PX

# Criando botões (mantido o mesmo, pois a interação é com as funções)
# L1 (Linha 0)
b1 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("%"),
    text= "%", 
    fg = "White",
    bg = cor2, 
    font=FONTE_OPERADORES
    )

b1.place(
    x = get_x_pos(0), 
    y = get_y_pos(0), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b2 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("√"),
    text = "√", 
    fg = "White", 
    bg = cor2, 
    font=FONTE_OPERADORES
    )

b2.place(
    x = get_x_pos(1), 
    y = get_y_pos(0), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b3 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("C"),
    text = "C", 
    fg = "White", 
    bg = cor2 ,
    font=FONTE_OPERADORES
    )

b3.place(
    x = get_x_pos(2), 
    y = get_y_pos(0), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b4 = Button(
    frameCorpo, 
    command = backspace, 
    text = "⌫", 
    fg = "White", 
    bg = cor2, 
    font=FONTE_OPERADORES
    )

b4.place(
    x = get_x_pos(3), 
    y = get_y_pos(0), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

# L2 (Linha 1)
b5 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("7"),
    text = "7", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b5.place(
    x = get_x_pos(0), 
    y = get_y_pos(1), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b6 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("8"),
    text = "8", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b6.place(
    x = get_x_pos(1), 
    y = get_y_pos(1), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b7 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("9"),
    text = "9", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b7.place(
    x = get_x_pos(2), 
    y = get_y_pos(1), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b8 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("/"),
    text = "÷", 
    fg = "White", 
    bg = cor2, 
    font=FONTE_OPERADORES
    )

b8.place(
    x = get_x_pos(3), 
    y = get_y_pos(1), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )


# L3 (Linha 2)
b9 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("4"),
    text = "4", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b9.place(
    x = get_x_pos(0), 
    y = get_y_pos(2), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b10 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("5"),
    text = "5", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b10.place(
    x = get_x_pos(1), 
    y = get_y_pos(2), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b11 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("6"),
    text = "6", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b11.place(
    x = get_x_pos(2),
    y = get_y_pos(2), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b12 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("*"),
    text = "x", 
    fg = "White", 
    bg = cor2, 
    font=FONTE_OPERADORES
    )

b12.place(
    x = get_x_pos(3), 
    y = get_y_pos(2), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

# L4 (Linha 3)
b13 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("1"),
    text = "1", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b13.place(
    x= get_x_pos(0),
    y= get_y_pos(3), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b14 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("2"),
    text = "2", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b14.place(
    x= get_x_pos(1), 
    y= get_y_pos(3), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b15 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("3"),
    text = "3", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b15.place(
    x= get_x_pos(2), 
    y= get_y_pos(3), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b16 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("-"),
    text = "-", 
    fg = "White", 
    bg = cor2, 
    font=FONTE_OPERADORES
    )

b16.place(
    x = get_x_pos(3), 
    y = get_y_pos(3), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )


# L5 (Linha 4)
b17 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("+/-"),
    text = "+/-", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b17.place(
    x= get_x_pos(0), 
    y= get_y_pos(4), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b18 = Button (
    frameCorpo, 
    command = lambda: entrar_valores("0"),
    text = "0", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b18.place(
    x= get_x_pos(1), 
    y= get_y_pos(4), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b19 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("+"),
    text = "+", 
    fg = "White", 
    bg = cor2, 
    font=FONTE_OPERADORES
    )

b19.place(
    x= get_x_pos(3), 
    y= get_y_pos(4), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b20= Button(
    frameCorpo, 
    command = lambda: entrar_valores("."),
    text = ",", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b20.place(
    x= get_x_pos(2), 
    y= get_y_pos(4), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )


# L6 (Linha 5)
b21 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("("), 
    text = "(", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b21.place(
    x = get_x_pos(0), 
    y = get_y_pos(5), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b22 = Button(
    frameCorpo, 
    command = lambda: entrar_valores(")"), 
    text = ")", 
    bg = cor1, 
    font=FONTE_NUMEROS
    )

b22.place(
    x= get_x_pos(1), 
    y= get_y_pos(5), 
    width=LARGURA_CELULA_PX, 
    height=ALTURA_CELULA_PX
    )

b23 = Button(
    frameCorpo, 
    command = lambda: entrar_valores("="),
    text = "=", 
    bg = cor4, 
    font=FONTE_IGUAL
    )

b23.place(
    x= get_x_pos(2), 
    y= get_y_pos(5), 
    width=LARGURA_CELULA_PX * 2, 
    height=ALTURA_CELULA_PX
    )

janela.mainloop()
