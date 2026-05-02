# GUI Architecture & Flow

This document outlines the Graphical User Interface (GUI) architecture, flow, and components of the **Warung+** (IWIK) application. The application is built using **PyQt6**, transitioning from standard Tkinter components to a modern, widget-based PyQt approach.

## 1. Application Entry Point (`main.py`)
The application initializes in `main.py`, which is responsible for:
- Parsing command-line arguments (e.g., `--dev`).
- Connecting to the SQLite database (`appdata.db` or `dev_data.db`).
- Setting up the `QApplication` and its core metadata (Application Name, Organization Name).
- Instantiating and showing the `App` (`AppShell`).

## 2. Core Layout

### `AppShell` (`gui/views/app_shell.py`)
The `AppShell` (aliased as `App`) is the top-level `QWidget` window. It uses a `QStackedWidget` to manage the high-level application states (the "screens").
The typical flow through the AppShell stack is:
1. **Splash Screen** (`SplashScreen`): Shown briefly to load assets and database context.
2. **User Selection** (`SelectUserScreen`): Allows the user to select an existing account to log into.
3. **Login Screen** (`LoginScreen`): PIN/Password entry.
4. **Add Admin Screen** (`AddAdminScreen`): State for adding a new administrative user.
5. **Main Shell** (`MainShell`): The core application dashboard when logged in.

### `MainShell` (`gui/views/main_shell.py`)
Once a user has successfully traversed the authentication flow, they enter the `MainShell`. 
- **Sidebar**: A consistent navigation pane on the left (`SidebarWidget`).
- **Content Area**: Another `QStackedWidget` on the right side that switches between different functional pages.

## 3. Screens & Pages

Located in `gui/views/screens/`. These are standalone widget views tailored to specific operations.

- **`splash_screen.py`**: Initial loader and branding setup.
- **`select_user_screen.py`**: Fetches users from `gui/models/user_model.py` and displays them as selectable profiles.
- **`login_screen.py`**: Handles authentication verification.
- **`add_admin_screen.py`**: A dedicated form for registering a new administrator if necessary or requested by the user flow.
- **`product_page.py`**: Specifically designed for managing products (viewing, adding, editing).

## 4. Reusable Components

Located in `gui/views/components/`. The GUI uses a component-driven structure to ensure consistency across the application.
- **`sidebar.py`**: The main navigation menu. Contains `NavItem` and `LogoutButton`.
- **`buttons.py`**: Themed interactive buttons (`PrimaryButton`, `GhostButton`).
- **`pin_row.py` & `pin_dot.py`**: Customized PIN entry components for the login screen.
- **`avatar.py` & `badge.py`**: Visual indicators for user profiles and roles.
- **`name_input.py`**: Styled input fields for forms.
- **`divider.py`**: Separators to manage spacing within layouts.

## 5. Model-View Separation
- **Views**: The GUI directly handles all presentation (`app_shell.py`, `components/*`, `screens/*`).
- **Models**: Database interactions for the GUI are mostly routed through dedicated controllers or GUI models (e.g., `gui/models/user_model.py` handles fetching/creating users).
- **Transitions**: Screen transitions inside `AppShell` and `MainShell` are performed by manipulating the index of the underlying `QStackedWidget`. The shell handles signals emitted from the child screens (e.g., `login_successful` signal transitioning the app to the `MainShell`).

## Conclusion
The UI provides a modern, single-page application (SPA) feel, relying heavily on `QStackedWidget` routing and reusable styling constructs, making it scalable to add more pages (Sales, Inventory, Reports) by simply injecting new views into the `MainShell` stack.
