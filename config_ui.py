"""Configuration UI component for the File Manager."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static, Switch

from config_manager import ConfigManager
from theme_manager import ThemeManager


class ConfigScreen(ModalScreen):
    """A modal screen for configuring application settings."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("ctrl+c", "dismiss", "Cancel"),
        Binding("f1", "save_and_close", "Save"),
        Binding("enter", "save_and_close", "Save"),
    ]

    def __init__(self, config: ConfigManager) -> None:
        """Initialize the configuration screen.
        
        Args:
            config: The configuration manager instance.
        """
        super().__init__()
        self.config = config
        self.theme_manager = ThemeManager()
        self._widgets = {}

    def compose(self) -> ComposeResult:
        """Create the configuration UI."""
        with Vertical(id="config-container"):
            yield Static("⚙️ Configuration", id="config-title")
            
            # Theme setting
            with Horizontal(id="theme-row"):
                yield Label("Theme:")
                # Theme buttons will be added dynamically in on_mount
            
            # Preview size limit
            with Horizontal(id="preview-size-row"):
                yield Label("Preview Size Limit (bytes):")
                yield Input(
                    value=str(self.config.preview_size_limit),
                    id="preview-size-input",
                    placeholder="1000000"
                )
            
            # Preview character limit
            with Horizontal(id="preview-char-row"):
                yield Label("Preview Character Limit:")
                yield Input(
                    value=str(self.config.get("preview_char_limit", 10000)),
                    id="preview-char-input",
                    placeholder="10000"
                )
            
            # Show hidden files
            with Horizontal(id="hidden-files-row"):
                yield Label("Show Hidden Files:")
                yield Switch(
                    value=self.config.show_hidden_files,
                    id="show-hidden-switch"
                )
            
            # Syntax highlighting
            with Horizontal(id="syntax-row"):
                yield Label("Syntax Highlighting:")
                yield Switch(
                    value=self.config.get("syntax_highlighting", True),
                    id="syntax-switch"
                )
            
            # Line numbers
            with Horizontal(id="line-numbers-row"):
                yield Label("Line Numbers:")
                yield Switch(
                    value=self.config.get("line_numbers", True),
                    id="line-numbers-switch"
                )
            
            # Confirm delete
            with Horizontal(id="confirm-delete-row"):
                yield Label("Confirm Delete:")
                yield Switch(
                    value=self.config.get("confirm_delete", True),
                    id="confirm-delete-switch"
                )
            
            # Auto refresh
            with Horizontal(id="auto-refresh-row"):
                yield Label("Auto Refresh:")
                yield Switch(
                    value=self.config.get("auto_refresh", True),
                    id="auto-refresh-switch"
                )
            
            # Ignored patterns
            with Vertical(id="ignored-patterns-row"):
                yield Label("Ignored Patterns (one per line):")
                yield Input(
                    value="\n".join(self.config.ignored_patterns),
                    id="ignored-patterns-input",
                    multiline=True
                )
            
            # Action buttons
            with Horizontal(id="action-buttons"):
                yield Button("💾 Save", id="save-button", variant="primary")
                yield Button("🔄 Reset to Defaults", id="reset-button")
                yield Button("❌ Cancel", id="cancel-button")

    def on_mount(self) -> None:
        """Initialize UI state when mounted."""
        self._create_theme_buttons()
        self._update_theme_buttons()
        self._focus_first_widget()

    def _create_theme_buttons(self) -> None:
        """Create theme buttons dynamically."""
        theme_row = self.query_one("#theme-row", Horizontal)
        
        # Add theme buttons
        for theme in self.theme_manager.list_themes():
            button = Button(
                theme.display_name,
                id=f"theme-{theme.name}",
                name=theme.name
            )
            theme_row.mount(button)
    
    def _update_theme_buttons(self) -> None:
        """Update theme button states."""
        current_theme = self.config.theme
        
        for theme in self.theme_manager.list_themes():
            try:
                button = self.query_one(f"#theme-{theme.name}", Button)
                if theme.name == current_theme:
                    button.variant = "primary"
                else:
                    button.variant = "default"
            except Exception:
                # Button might not exist yet, skip
                pass

    def _focus_first_widget(self) -> None:
        """Focus the first input widget."""
        themes = self.theme_manager.list_themes()
        if themes:
            first_theme = themes[0]
            try:
                button = self.query_one(f"#theme-{first_theme.name}", Button)
                button.focus()
            except Exception:
                # Fallback to preview size input
                try:
                    self.query_one("#preview-size-input", Input).focus()
                except Exception:
                    pass

    def action_save_and_close(self) -> None:
        """Save configuration and close the screen."""
        try:
            self._save_settings()
            self.dismiss(result=True)
        except ValueError as e:
            self._show_error(str(e))

    def action_dismiss(self) -> None:
        """Dismiss the screen without saving."""
        self.dismiss(result=False)

    def _save_settings(self) -> None:
        """Save all settings from the UI to the config."""
        # Save theme
        theme_buttons = self.query("Button[name^='theme-']")
        for btn in theme_buttons:
            if btn.variant == "primary":
                self.config.set("theme", btn.name.replace("theme-", ""))
                break

        # Save preview size limit
        preview_input = self.query_one("#preview-size-input", Input)
        try:
            preview_size = int(preview_input.value)
            self.config.set("preview_size_limit", preview_size)
        except ValueError as err:
            raise ValueError("Preview size limit must be a valid integer") from err

        # Save preview character limit
        char_input = self.query_one("#preview-char-input", Input)
        try:
            char_limit = int(char_input.value)
            self.config.set("preview_char_limit", char_limit)
        except ValueError as err:
            raise ValueError("Preview character limit must be a valid integer") from err

        # Save boolean settings
        self.config.set("show_hidden_files",
                       self.query_one("#show-hidden-switch", Switch).value)
        self.config.set("syntax_highlighting",
                       self.query_one("#syntax-switch", Switch).value)
        self.config.set("line_numbers",
                       self.query_one("#line-numbers-switch", Switch).value)
        self.config.set("confirm_delete",
                       self.query_one("#confirm-delete-switch", Switch).value)
        self.config.set("auto_refresh",
                       self.query_one("#auto-refresh-switch", Switch).value)

        # Save ignored patterns
        patterns_input = self.query_one("#ignored-patterns-input", Input)
        patterns = [p.strip() for p in patterns_input.value.split("\n") if p.strip()]
        self.config.set("ignored_patterns", patterns)

    def _show_error(self, message: str) -> None:
        """Show an error message."""
        # For now, just update the title to show the error
        title = self.query_one("#config-title", Static)
        title.update(f"❌ Error: {message}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id

        if button_id == "save-button":
            self.action_save_and_close()
        elif button_id == "reset-button":
            self._reset_to_defaults()
        elif button_id == "cancel-button":
            self.action_dismiss()
        elif button_id.startswith("theme-"):
            self._select_theme_button(event.button.name)

    def _select_theme_button(self, theme: str) -> None:
        """Select a theme button."""
        # Reset all theme buttons to default
        for theme_obj in self.theme_manager.list_themes():
            try:
                button = self.query_one(f"#theme-{theme_obj.name}", Button)
                button.variant = "default"
            except Exception:
                pass
        
        # Set selected theme button to primary
        try:
            selected_button = self.query_one(f"#theme-{theme}", Button)
            selected_button.variant = "primary"
        except Exception:
            pass

    def _reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.config.reset_all()
        
        # Update UI to reflect defaults
        self._update_theme_buttons()
        
        # Update input fields
        preview_input = self.query_one("#preview-size-input", Input)
        preview_input.value = str(self.config.preview_size_limit)
        
        char_input = self.query_one("#preview-char-input", Input)
        char_input.value = str(self.config.get("preview_char_limit", 10000))
        
        # Update switches
        self.query_one("#show-hidden-switch", Switch).value = self.config.show_hidden_files
        self.query_one("#syntax-switch", Switch).value = self.config.get("syntax_highlighting", True)
        self.query_one("#line-numbers-switch", Switch).value = self.config.get("line_numbers", True)
        self.query_one("#confirm-delete-switch", Switch).value = self.config.get("confirm_delete", True)
        self.query_one("#auto-refresh-switch", Switch).value = self.config.get("auto_refresh", True)
        
        # Update ignored patterns
        patterns_input = self.query_one("#ignored-patterns-input", Input)
        patterns_input.value = "\n".join(self.config.ignored_patterns)
        
        # Show success message
        title = self.query_one("#config-title", Static)
        title.update("✅ Reset to defaults")

    def _css(self) -> str:
        """Return CSS styles for the configuration screen."""
        return """
        #config-container {
            layout: vertical;
            padding: 2;
            background: $surface;
            border: thick $primary;
            width: 80%;
            height: 90%;
            margin: 1 1;
        }

        #config-title {
            text-align: center;
            text-style: bold;
            margin: 1 0;
            color: $primary;
        }

        Horizontal {
            height: auto;
            padding: 1 0;
            align: left middle;
        }

        Label {
            width: 25%;
            text-align: right;
            margin-right: 2;
        }

        Button {
            margin-right: 1;
        }

        Input {
            width: 40%;
        }

        #ignored-patterns-input {
            width: 60%;
            height: 8;
        }

        #action-buttons {
            margin-top: 2;
            padding-top: 2;
            border-top: solid $panel;
            justify-content: center;
        }

        #action-buttons Button {
            margin: 0 1;
        }

        Switch {
            margin-right: 2;
        }
        """
