import flet as ft 
from sympy import sympify, N
from datetime import datetime 
import json 

def main(page: ft.Page):
    page.title = "Calculex"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.bgcolor = ft.colors.BLACK
    #page.window_title_bar_hidden = False
    #page.window_frameless = True
    #page.window_width = 300
    #page.window_height = 600
    #page.window_resizable = True
    #page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    #page.window_icon = "calculator.svg"

    current_expression = ""
    result_display = ft.Text(value="0", color=ft.colors.WHITE, size=20) 
    expression_display = ft.Text(value="", color=ft.colors.WHITE, size=14) 
    # clear_button = ft.ElevatedButton(text="AC", on_click=None) 
    history = []
    history_visible = False 
    history_key = "calc_history" 

    def load_history():
        history_json = page.client_storage.get(history_key) 
        if history_json: 
            return json.loads(history_json) 
        return [] 

    def save_history():
        page.client_storage.set(history_key, json.dumps(history)) #utiliza o dumps para armazenar o conteudo presente na chave dentro do arquivo json, em forma de uma string json

    def format_number(number):
        try:
            num = float(number)
            if num.is_integer():
                return "{:,.0f}".format(int(num)).replace(",", ".") #esse replace é unicamente utilizado para questões visuais
            else:
                parts = "{:,.10f}".format(num).split(".")
                integer_part = parts[0].replace(",", ".") #esse tambem é para qeustões visuais
                decimal_part = parts[1].rstrip("0")
                return f"{integer_part},{decimal_part}" if decimal_part else integer_part

        except ValueError:
            return "Erro"


    def calculate_expression():
        nonlocal current_expression #referenciamos a variavel que é declarada dentro da função main
        try:
            current_expression = current_expression.replace(",", ".") 

            if "%" in current_expression:
                value = current_expression.replace("%", "") #retira o simbolo de % e deixa um espaço vazio
                result = N(sympify(value) / 100, 10) #efetua a conta normalmente com o valor atual
                result_str = format_number(result) #formata o resultado encontrado
                result_display.value = result_str #mostra esse resultado no display
                add_to_history(current_expression, result_str) #adiciona oo calculo no historico
                current_expression = result_str #no caso da porcentagem atualiza o campo de expressão para, quando dar continuidade no calculo atualiza a expressão para decimal ao invés de manter em porcentagem, é mais para uma questão visual do que outra coisa
            else: #segue a mesma logica do if
                expr = current_expression.replace("√", "sqrt") #faz essa troca pra depois utilizar o sympify que vai reconhecer o sqrt como a função utilizada para calcular raiz quadradas e assim efetuar o calculo até 10 casas decimais
                result = N(sympify(expr), 10)
                result_str = format_number(result)
                result_display.value = result_str
                add_to_history(current_expression, result_str)
            clear_button.text = "AC" #modifica o botão da expressão
            page.update() #atualiza a pagina
        except Exception as e: #trata das exceções, qualquer expressão mal construida ou um numero mal inserido
            result_display.value = "Erro" #mostra erro como mensagem
            page.update() #atualiza a pagina

    def add_to_history(expression, result): #onde iremos adicionar a expressão e seu devido resultado
        if len(history) >= 10: #se tiver mais de 10 itens faz pop do ultimo item da lista
            history.pop()
        for item in history:
            item["index"] += 1 #atualiza o indice de cada item do historico, pra quando for adicionado um valor se ajustar conforme a quantidade de objetos
        history.insert(0, {
            "index": 1,
            "timestamp": datetime.now().strftime("%Y-%m-%D %H:%M:%S"),
            "expression": expression,
            "result": result
        })
        save_history() #faz o jump no arquivo de json, para podermos acessar sempre que reabrimos a aplicação, caso exista alguma informação dela
        update_history_display() # atualiza visualmente o displau do historico

    def update_history_display():
        history_column.controls.clear() #entendi mas vou ter que estudar um pouquinho mais sobre
        for item in history:
            history_column.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(f"{item['index']}. {item['timestamp']}", color=ft.colors.WHITE, size=12),
                        ft.Text(f"{item['expression']} = {item['result']}", color=ft.colors.WHITE, size=12),
                        ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, item=item: delete_history_item(item)),
                        ft.IconButton(icon=ft.icons.ADD, on_click=lambda e, item=item: use_history_item(item)),
                    ],
                    scroll=ft.ScrollMode.ALWAYS,
                )
            )
        page.update()

    def delete_history_item(item):
        history.remove(item)
        save_history()
        update_history_display()

    def use_history_item(item):
        nonlocal current_expression
        current_expression = item["expression"]
        expression_display.value = current_expression
        page.update()

    def toggle_history(): #alterna a visibilidade do historico, se é falso vira true se é true vira falso
        nonlocal history_visible
        history_visible = not history_visible
        history_container.visible = history_visible
        page.update()

    def update_expression(value):
        nonlocal current_expression
        current_expression += value #adiciona o valor do botão pressionado na expressão
        expression_display.value = current_expression #mostra a expressão completa no display
        clear_button.text = "C" #modifica o sinal do botão de AC para C indicando que agora tem algo que pode ser apagado
        page.update()

    def clear_expression():
        nonlocal current_expression
        if clear_button.text == "AC": 
            current_expression = ""
            expression_display.value = ""
            result_display.value = "0"
        else:
            current_expression = current_expression[:-1] #faz slicing da string para apagar o ultimo caracter
            expression_display.value = current_expression #atualiza a expressão 
        clear_button.text = "AC" if not current_expression else "C" #se a expressão estiver vazia troca pra AC se não mantém como C<
        page.update()

    def clear_entry():
    #    nonlocal current_expression
    #    if current_expression:
    #        current_expression = ""
    #        expression_display.value = ""
    #        result_display.value = "0"
    #        page.update()

        nonlocal current_expression
        if current_expression:
            # Remove espaços e percorre a string de trás pra frente
            i = len(current_expression) - 1
            while i >= 0 and (current_expression[i].isdigit() or current_expression[i] in ",."):
                i -= 1
            current_expression = current_expression[:i+1]  # mantém tudo até o último operador
            expression_display.value = current_expression
            result_display.value = "0"
            page.update()

    def invert_sign():
        nonlocal current_expression
        if current_expression:
            try:
                current_expression = f"({current_expression})*-1"
                expression_display.value = current_expression
                page.update()
            except Exception as e:
                result_display.value = "Erro"
                page.update()

    def calculate_sqrt():
        nonlocal current_expression
        if current_expression:
            current_expression = f"√({current_expression})"
            expression_display.value = current_expression
            page.update()

    def calculate_percentage():
        nonlocal current_expression
        if current_expression:
            current_expression += "%"
            expression_display.value = current_expression
            page.update()

    def calculate_inverse():
        nonlocal current_expression
        try:
            result = 1 / sympify(current_expression)
            current_expression = str(result)
            expression_display.value = current_expression
            page.update()
        except Exception as e:
            result_display.value = "Erro"
            page.update()

    def calculate_power():
        nonlocal current_expression
        if current_expression:
            current_expression += "^"
            expression_display.value = current_expression
            page.update()

    def calculate_factorial():
        nonlocal current_expression
        if current_expression:
            current_expression += "!"
            expression_display.value = current_expression
            page.update()

    def toggle_parentheses(button):
        if button.text == "(":
            update_expression("(")
            button.text = ")"
        else:
            update_expression(")")
            button.text = "("
        page.update()

    class CalcButton(ft.ElevatedButton):
        def __init__(self, text, expand=1, on_click=None, bgcolor=ft.colors.GREY_900, color=ft.colors.WHITE):
            super().__init__()
            self.text = text
            self.expand = expand
            self.on_click = on_click
            self.bgcolor = bgcolor
            self.color = color
            self.shape = ft.RoundedRectangleBorder(radius=10)
            self.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.GREY_800,
                offset=ft.Offset(2, 2),
            )

    class DigitButton(CalcButton):
        def __init__(self, text, expand=1):
            super().__init__(text, expand, on_click=lambda e: update_expression(text), bgcolor=ft.colors.GREY_900, color=ft.colors.WHITE)

    class ActionButton(CalcButton):
        def __init__(self, text, on_click=None):
            super().__init__(text, on_click=on_click, bgcolor=ft.colors.DEEP_ORANGE, color=ft.colors.WHITE)

    class ExtraActionButton(CalcButton):
        def __init__(self, text, on_click=None):
            super().__init__(text, on_click=on_click, bgcolor=ft.colors.GREY_800, color=ft.colors.WHITE)

    clear_button = ExtraActionButton(text="AC", on_click=lambda e: clear_expression())
    clear_entry_button = ExtraActionButton(text="CE", on_click=lambda e: clear_entry())
    parentheses_button = ExtraActionButton(text="(", on_click=lambda e: toggle_parentheses(parentheses_button))
    history_button = ExtraActionButton(text="Histórico", on_click=lambda e: toggle_history())

    history = load_history()
    history_column = ft.Column(scroll=ft.ScrollMode.ALWAYS)
    history_container = ft.Container(
        content=ft.ListView(
            controls=[history_column],
            height=200,
            spacing=10,
        ),
        visible=False,
        padding=10,
        bgcolor=ft.colors.GREY_900,
        border_radius=ft.border_radius.all(10),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.colors.GREY_800,
            offset=ft.Offset(2, 2),
        ),
    )

    page.add(
        ft.Container(
            width=350,
            bgcolor=ft.colors.GREY_900,
            border_radius=ft.border_radius.all(20),
            padding=20,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.GREY_800,
                offset=ft.Offset(4, 4),
            ),
            content=ft.Column(
                controls=[
                    ft.Row(controls=[expression_display], alignment="end"),
                    ft.Row(controls=[result_display], alignment="end"),
                    ft.Row(
                        controls=[
                            clear_button,
                            clear_entry_button,
                            ExtraActionButton(text="+/-", on_click=lambda e: invert_sign()),
                            ExtraActionButton(text="%", on_click=lambda e: calculate_percentage()),
                            ExtraActionButton(text="!", on_click=lambda e: calculate_factorial()),
                            parentheses_button,
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ExtraActionButton(text="√", on_click=lambda e: calculate_sqrt()),
                            ExtraActionButton(text="1/x", on_click=lambda e: calculate_inverse()),
                            ExtraActionButton(text="x^y", on_click=lambda e: calculate_power()),
                            ActionButton(text="/", on_click=lambda e: update_expression("/")),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            DigitButton(text="7"),
                            DigitButton(text="8"),
                            DigitButton(text="9"),
                            ActionButton(text="*", on_click=lambda e: update_expression("*")),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            DigitButton(text="4"),
                            DigitButton(text="5"),
                            DigitButton(text="6"),
                            ActionButton(text="-", on_click=lambda e: update_expression("-")),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            DigitButton(text="1"),
                            DigitButton(text="2"),
                            DigitButton(text="3"),
                            ActionButton(text="+", on_click=lambda e: update_expression("+")),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            DigitButton(text="0", expand=2),
                            DigitButton(text=","),
                            ActionButton(text="=", on_click=lambda e: calculate_expression()),
                        ]
                    ),
                    history_button,
                    history_container,
                ]
            ),
        )
    )

ft.app(target=main, view=ft.WEB_BROWSER, host="0.0.0.0", port=8550)
#ft.app(target=main, view=ft.FLET_APP)
