import httpx
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Input, ListView, ListItem
from textual.screen import ModalScreen

API_BASE = "http://localhost:8000/api/todos"


class TodoItem(ListItem):
    """A single todo row in the list."""

    def __init__(self, todo: dict) -> None:
        super().__init__()
        self.todo = todo

    def compose(self) -> ComposeResult:
        check = "[x]" if self.todo["completed"] else "[ ]"
        title = self.todo["title"]
        if self.todo["completed"]:
            title = f"[strike]{title}[/strike]"
        yield Static(f" {check}  {title}", markup=True)


class AddScreen(ModalScreen[str]):
    """Modal for adding a new todo."""

    BINDINGS = [Binding("escape", "dismiss", "Cancel")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(" New Todo", classes="modal-title"),
            Input(placeholder="What needs to be done?", id="add-input"),
            Static(" [Enter] Save  [Esc] Cancel", classes="modal-hint"),
            classes="modal-box",
        )

    def on_mount(self) -> None:
        self.query_one("#add-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if value:
            self.dismiss(value)
        else:
            self.dismiss(None)


class TodoApp(App):
    """Terminal UI for the todo list."""

    CSS = """
    Screen {
        background: $surface;
    }
    ListView {
        height: 1fr;
        margin: 1 2;
    }
    ListItem {
        padding: 0 1;
    }
    ListItem > Static {
        width: 1fr;
    }
    .modal-box {
        width: 60;
        height: auto;
        max-height: 10;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        margin: 4 0;
        align: center middle;
    }
    .modal-title {
        text-style: bold;
        margin-bottom: 1;
    }
    .modal-hint {
        color: $text-muted;
        margin-top: 1;
    }
    #status {
        dock: bottom;
        height: 1;
        padding: 0 2;
        color: $text-muted;
        background: $surface-darken-1;
    }
    """

    TITLE = "Todo"
    BINDINGS = [
        Binding("a", "add", "Add"),
        Binding("space", "toggle", "Toggle"),
        Binding("d", "delete", "Delete"),
        Binding("r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(id="todo-list")
        yield Static("", id="status")
        yield Footer()

    async def on_mount(self) -> None:
        await self.refresh_todos()

    async def refresh_todos(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(API_BASE)
                resp.raise_for_status()
                todos = resp.json()
        except httpx.ConnectError:
            self.query_one("#status", Static).update(
                " Could not connect to server. Is it running?"
            )
            return

        lv = self.query_one("#todo-list", ListView)
        lv.clear()
        for todo in todos:
            lv.append(TodoItem(todo))

        remaining = sum(1 for t in todos if not t["completed"])
        self.query_one("#status", Static).update(
            f" {remaining} remaining of {len(todos)} total"
        )

    async def action_add(self) -> None:
        title = await self.push_screen_wait(AddScreen())
        if title:
            async with httpx.AsyncClient() as client:
                await client.post(API_BASE, json={"title": title})
            await self.refresh_todos()

    async def action_toggle(self) -> None:
        lv = self.query_one("#todo-list", ListView)
        if lv.highlighted_child and isinstance(lv.highlighted_child, TodoItem):
            todo_id = lv.highlighted_child.todo["id"]
            async with httpx.AsyncClient() as client:
                await client.put(f"{API_BASE}/{todo_id}", json={})
            await self.refresh_todos()

    async def action_delete(self) -> None:
        lv = self.query_one("#todo-list", ListView)
        if lv.highlighted_child and isinstance(lv.highlighted_child, TodoItem):
            todo_id = lv.highlighted_child.todo["id"]
            async with httpx.AsyncClient() as client:
                await client.delete(f"{API_BASE}/{todo_id}")
            await self.refresh_todos()

    async def action_refresh(self) -> None:
        await self.refresh_todos()


if __name__ == "__main__":
    TodoApp().run()
