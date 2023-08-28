from dataclasses import dataclass, field

from nicegui import ui

ui.dark_mode(True)


# ========
# Thoughts
# ========
# Idea 1: Use the glisser-déposer? Yeah but 1/ harder to code and 2/ ugly in responsive design
# Idea 2: 


# =========
# Functions
# =========



# ==========
# Parameters
# ==========
color_blue = "#5898d4"


# ==
# UI
# ==
ui.label("Today's list").classes(f"text-2xl text-[{color_blue}]")
with ui.card():
    pass



# ===
# Run
# ===
ui.run()
