from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.align import Align

# Tema personalizado para elegancia
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "header": "bold magenta",
    "accent": "bold cyan",
})

console = Console(theme=custom_theme)

def print_header():
    ascii_art = """
    ██████╗ ██████╗ ███████╗███╗   ██╗ ██████╗  ██████╗ ██████╗ ███████╗
    ██╔══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝ ██╔═══██╗██╔══██╗██╔════╝
    ██║  ██║██████╔╝█████╗  ██╔██╗ ██║██║      ██║   ██║██║  ██║█████╗  
    ██║  ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║      ██║   ██║██║  ██║██╔══╝  
    ██████╔╝██║     ███████╗██║ ╚████║╚██████╗ ╚██████╔╝██████╔╝███████╗
    ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝
    """
    console.print(Align.center(f"[accent]{ascii_art}[/accent]"))
    
    header_text = Text("MULTI-AGENT ORCHESTRATION SYSTEM", style="info")
    panel = Panel(
        Align.center(header_text),
        border_style="dim",
        padding=(0, 2),
        subtitle="[bold]OP EN CO DE[/bold]",
        subtitle_align="center"
    )
    console.print(panel)

def print_agent_status(agents_data):
    table = Table(title="Agentes Activos", border_style="dim")
    table.add_column("Agente", style="accent")
    table.add_column("Rol", style="info")
    table.add_column("Modelo", style="white")
    table.add_column("Estado", justify="center")

    for agent in agents_data:
        table.add_row(
            agent['name'],
            agent['role'],
            agent['model'],
            "[bold green]● Activo[/bold green]"
        )
    
    console.print(table)

def print_step(message):
    console.print(Panel(message, border_style="info", expand=False))

def print_success(message):
    console.print(f"[success]✔[/success] {message}")

def print_error(message):
    console.print(f"[error]✖[/error] {message}")
