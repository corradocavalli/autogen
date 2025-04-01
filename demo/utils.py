from rich import print


def print_core(message: str):
    print(f"[bold magenta italic]{message}[/bold magenta italic]")


def print_info(message: str):
    print(f"[bold gray italic]{message}[/bold gray italic]")


def print_error(message: str):
    print(f"[bold red]{message}[/bold red]")


def print_assistant(sender: str, receiver: str, message: str):
    print(
        f"[bold green italic]({sender}->{receiver}):[/bold green italic] [bold cyan]{message}[/bold cyan]"
    )


def print_tool(tool: str, params: str):
    print(f"[bold blue]Tool ({tool}) invoked with: {params}[/bold blue]")


def print_route(sender: str, receiver, message: str):
    print(
        f"[bold green italic]({sender}->{receiver}):[/bold green italic] [orange]{message}[/orange]"
    )
