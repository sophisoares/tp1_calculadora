import flet as ft
from sympy import sympify, N

def main(page: ft.Page):
    page.title = "Calc App"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.bgcolor = ft.Colors.BLACK

    
    current_expression = ""
    result_display = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
    expression_display = ft.Text(value="", color=ft.Colors.WHITE, size=14)

    
    def calculate_expression():
        nonlocal current_expression
        try:
            result = N(sympify(current_expression), 10)  # Avalia a expressão com 10 dígitos de precisão
            result_display.value = str(result)
        except Exception as e:
            result_display.value = "Erro"
        page.update()

    
    def update_expression(value):
        nonlocal current_expression
        current_expression += value
        expression_display.value = current_expression
        page.update()

    
    def clear_expression():
        nonlocal current_expression
        current_expression = ""
        expression_display.value = ""
        result_display.value = "0"
        page.update()

    
    class CalcButton(ft.ElevatedButton):
        def __init__(self, text, expand=1, on_click=None):
            super().__init__()
            self.text = text
            self.expand = expand
            self.on_click = on_click

    class DigitButton(CalcButton):
        def __init__(self, text, expand=1):
            CalcButton.__init__(self, text, expand, on_click=lambda e: update_expression(text))
            self.bgcolor = ft.Colors.WHITE24
            self.color = ft.Colors.WHITE

    class ActionButton(CalcButton):
        def __init__(self, text, on_click=None):
            CalcButton.__init__(self, text, on_click=on_click)
            self.bgcolor = ft.Colors.ORANGE
            self.color = ft.Colors.WHITE

    class ExtraActionButton(CalcButton):
        def __init__(self, text, on_click=None):
            CalcButton.__init__(self, text, on_click=on_click)
            self.bgcolor = ft.Colors.BLUE_GREY_100
            self.color = ft.Colors.BLACK

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
                            ExtraActionButton(text="AC", on_click=lambda e: clear_expression()),
                            ExtraActionButton(text="⬅️", on_click=lambda e: update_expression("⬅️")),
                            ExtraActionButton(text="%", on_click=lambda e: update_expression("%")),
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
                            DigitButton(text="."),
                            ActionButton(text="=", on_click=lambda e: calculate_expression()),
                        ]
                    ),
                ]
            ),
        )
    )

ft.app(target=main)