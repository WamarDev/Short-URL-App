import reflex as rx
import random
import string

# 1. LA BASE DE DATOS
# Creamos una tabla para guardar la relación: Código Corto <-> URL Larga
class Url(rx.Model, table=True):
    original_url: str
    short_code: str

# 2. EL ESTADO (LA LÓGICA)
class State(rx.State):
    current_url: str = ""  # Lo que el usuario escribe en el input
    generated_link: str = "" # El resultado final

    def create_short_url(self):
        """Genera un código aleatorio y guarda la URL en la base de datos"""
        if self.current_url == "":
            return # No hacemos nada si está vacío

        # Generamos un código aleatorio de 6 letras (ej: "Axy91z")
        chars = string.ascii_letters + string.digits
        code = "".join(random.choice(chars) for _ in range(6))

        # Guardamos en la Base de Datos
        # "with rx.session() as session" maneja la conexión segura
        with rx.session() as session:
            new_entry = Url(original_url=self.current_url, short_code=code)
            session.add(new_entry)
            session.commit()

        # Preparamos el link para mostrarlo al usuario
        # En local será localhost:3000/[codigo]
        self.generated_link = f"http://localhost:3000/{code}"
    
    @rx.var
    def show_result(self) -> bool:
        """Variable calculada para saber si mostramos el resultado o no"""
        return self.generated_link != ""

    def handle_redirect(self):
        """Esta función se ejecuta cuando alguien entra a la URL corta"""
        # Obtenemos el código de la URL (ej: Axy91z)
        code = self.router.page.params.get("code")
        
        # Buscamos en la base de datos
        with rx.session() as session:
            result = session.exec(
                Url.select().where(Url.short_code == code)
            ).first()
            
            # Si existe, redirigimos a la web original
            if result:
                return rx.redirect(result.original_url)
            else:
                return rx.window_alert("¡Ese enlace no existe!")

# 3. LA INTERFAZ VISUAL (Frontend)
def index():
    return rx.center(
        rx.vstack(
            rx.heading("✂️ Acortador de URLs", size="8"),
            rx.text("Convierte enlaces largos en cortos al instante."),
            
            # Zona de Input
            rx.hstack(
                rx.input(
                    placeholder="Pega tu URL larga aquí (ej: https://google.com)...",
                    on_change=State.set_current_url,
                    width="300px"
                ),
                rx.button("Acortar", on_click=State.create_short_url),
            ),

            # Zona de Resultado (Solo se ve si ya acortamos algo)
            rx.cond(
                State.show_result,
                rx.vstack(
                    rx.text("¡Tu enlace corto está listo! 👇", font_weight="bold"),
                    rx.code(State.generated_link, font_size="1.2em"),
                    rx.button("Copiar", on_click=rx.set_clipboard(State.generated_link)),
                    spacing="2",
                    align_items="center",
                    margin_top="20px",
                )
            ),
            spacing="5",
            align_items="center",
        ),
        height="100vh",
    )

# 4. PÁGINA DE REDIRECCIÓN (Invisible)
# Esta página no tiene interfaz, solo lógica
def redirect_page():
    return rx.center(rx.spinner()) # Muestra un circulito mientras redirige

# 5. CONFIGURACIÓN DE RUTAS
app = rx.App()
app.add_page(index, route="/") # Página principal
# Ruta dinámica: [code] captura cualquier cosa que pongas después de la barra
app.add_page(redirect_page, route="/[code]", on_load=State.handle_redirect)