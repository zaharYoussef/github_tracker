import curses


def select_repos_curses(repos):
    """Allow the user to select repositories interactively in the terminal using curses."""
    def menu(stdscr):
        curses.curs_set(0)
        current_row = 0
        selected_repos = []

        while True:
            stdscr.clear()

            # Display instructions
            stdscr.addstr(0, 0, "Use UP/DOWN to navigate, SPACE to select, and ENTER to confirm.")
            stdscr.addstr(1, 0, f"{'=' * 60}")

            # Render the menu
            for idx, repo in enumerate(repos):
                if idx == current_row:
                    stdscr.addstr(idx + 2, 0, f"> {repo}", curses.color_pair(1))
                else:
                    stdscr.addstr(idx + 2, 0, f"  {repo}")

                # Mark selected repos
                if repo in selected_repos:
                    stdscr.addstr(idx + 2, 60, "[SELECTED]")

            stdscr.refresh()

            # Handle key presses
            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(repos) - 1:
                current_row += 1
            elif key == ord(" "):  # Toggle selection with SPACE
                repo = repos[current_row]
                if repo in selected_repos:
                    selected_repos.remove(repo)
                else:
                    selected_repos.append(repo)
            elif key == 10:  # Enter key to confirm
                return selected_repos

    return curses.wrapper(menu)
