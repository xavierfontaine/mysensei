"""
Text utils
"""
import re

def replace_linebreaks_w_br(s):
    """Replace \n with <br>. Useful when leveraging nicegui.ui.markdown"""
    return re.sub(r'(?<!\n)\n(?!\n)', '<br>', s)
