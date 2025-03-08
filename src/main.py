import flet as ft
from sympy import sympify, N
from datetime import datetime
import json

def main(page: ft.Page):
    page.title = "Calc App"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.bgcolor = ft.Colors.BLACK

    current_expression = ""
    result_display = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
    expression_display = ft.Text(value="", color=ft.Colors.WHITE, size=14)
    clear_button = ft.ElevatedButton(text="AC", on_click=None)
    history = []
    history_visible = False
    history_key = "calc_history"

    def load_history():
        history_json = page.client_storage.get(history_key)
        if history_json:
            return json.loads(history_json)
        return []

    def save_history():
        page.client_storage.set(history_key, json.dumps(history))

    def format_number(number):
        try:
            num = float(number)
            if num.is_integer():
                return "{:,.0f}".format(int(num)).replace(",", ".")
            else:
                parts = "{:,.10f}".format(num).split(".")
                integer_part = parts[0].replace(",", ".")
                decimal_part = parts[1].rstrip("0")
                return f"{integer_part},{decimal_part}" if decimal_part else integer_part
        except ValueError:
            return number

    def calculate_expression():
        nonlocal current_expression
        try:
            if "%" in current_expression:
                value = current_expression.replace("%", "")
                result = N(sympify(value) / 100, 10)
                result_str = format_number(result)
                result_display.value = result_str
                add_to_history(current_expression, result_str)
                current_expression = result_str
            else:
                expr = current_expression.replace("√", "sqrt")
                result = N(sympify(expr), 10)
                result_str = format_number(result)
                result_display.value = result_str
                add_to_history(current_expression, result_str)
            clear_button.text = "AC"
            page.update()
        except Exception as e:
            result_display.value = "Erro"
            page.update()

    def add_to_history(expression, result):
       
        if len(history) >= 10:
            history.pop() 
        
        for item in history:
            item["index"] += 1
        
        history.insert(0, {
            "index": 1, 
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "expression": expression,
            "result": result
        })
        
        save_history() 
        update_history_display()  

    def update_history_display():
        history_column.controls.clear()
        for item in history:
            history_column.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(f"{item['index']}. {item['timestamp']}", color=ft.Colors.WHITE, size=12),
                        ft.Text(f"{item['expression']} = {item['result']}", color=ft.Colors.WHITE, size=12),
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

    def toggle_history():
        nonlocal history_visible
        history_visible = not history_visible
        history_container.visible = history_visible
        page.update()

    def update_expression(value):
        nonlocal current_expression
        current_expression += value
        expression_display.value = current_expression
        clear_button.text = "C"
        page.update()

    def clear_expression():
        nonlocal current_expression
        if clear_button.text == "AC":
            current_expression = ""
            expression_display.value = ""
            result_display.value = "0"
        else:
            current_expression = current_expression[:-1]
            expression_display.value = current_expression
        clear_button.text = "AC" if not current_expression else "C"
        page.update()

    def clear_entry():
        nonlocal current_expression
        if current_expression:
            current_expression = ""
            expression_display.value = ""
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
        def __init__(self, text, expand=1, on_click=None, bgcolor=ft.Colors.WHITE24, color=ft.Colors.WHITE):
            super().__init__()
            self.text = text
            self.expand = expand
            self.on_click = on_click
            self.bgcolor = bgcolor
            self.color = color

    class DigitButton(CalcButton):
        def __init__(self, text, expand=1):
            super().__init__(text, expand, on_click=lambda e: update_expression(text), bgcolor=ft.Colors.WHITE24, color=ft.Colors.WHITE)

    class ActionButton(CalcButton):
        def __init__(self, text, on_click=None):
            super().__init__(text, on_click=on_click, bgcolor=ft.Colors.ORANGE, color=ft.Colors.WHITE)

    class ExtraActionButton(CalcButton):
        def __init__(self, text, on_click=None):
            super().__init__(text, on_click=on_click, bgcolor=ft.Colors.BLUE_GREY_100, color=ft.Colors.BLACK)

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
        bgcolor=ft.Colors.BLACK,
        border_radius=ft.border_radius.all(10),
    )

    page.add(
        ft.Container(
            width=350,
            bgcolor=ft.Colors.BLACK,
            border_radius=ft.border_radius.all(20),
            padding=20,
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

ft.app(target=main)