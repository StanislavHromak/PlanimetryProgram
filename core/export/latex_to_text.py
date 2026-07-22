import re


def _find_matching_brace(s: str, open_idx: int) -> int:
    """Індекс закриваючої '}' для відкриваючої на позиції open_idx, з урахуванням вкладеності."""
    depth = 0
    i = open_idx
    while i < len(s):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(s) - 1  # захист від незакритої дужки


def _extract_arg(s: str, i: int) -> tuple[str, int]:
    """Аргумент команди: вміст {...} (з урахуванням вкладеності) або один символ, якщо без дужок."""
    if i < len(s) and s[i] == '{':
        close = _find_matching_brace(s, i)
        return s[i + 1:close], close + 1
    if i < len(s):
        return s[i], i + 1
    return '', i


def _replace_command_with_args(s: str, command: str, arg_count: int, template) -> str:
    """Знаходить усі входження команди (напр. '\\frac') з arg_count аргументами і замінює за шаблоном."""
    result = []
    i = 0
    while i < len(s):
        if s.startswith(command, i):
            j = i + len(command)
            args = []
            ok = True
            for _ in range(arg_count):
                if j >= len(s):
                    ok = False
                    break
                arg, j = _extract_arg(s, j)
                args.append(arg)
            if ok:
                result.append(template(*args))
                i = j
                continue
        result.append(s[i])
        i += 1
    return ''.join(result)


def _strip_script_braces(s: str) -> str:
    """
    Розкриває X_{вміст} та X^{вміст} у X_вміст / X^вміст (з урахуванням вкладеності),
    щоб наступні \\frac/\\sqrt/\\text коректно розпізнавали свої аргументи навіть тоді,
    коли всередині є підрядковий індекс із власними дужками (напр. \\frac{d_{min}}{d_{max}}).
    """
    result = []
    i = 0
    while i < len(s):
        if s[i] in ('_', '^') and i + 1 < len(s) and s[i + 1] == '{':
            close = _find_matching_brace(s, i + 1)
            result.append(s[i])
            result.append(s[i + 2:close])
            i = close + 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


_SYMBOLS = {
    r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\varphi': 'φ',
    r'\Sigma': 'Σ', r'\pi': 'π',
    r'\cdot': '*', r'\times': '*',
    r'\left': '', r'\right': '',
    r'\sin': 'sin', r'\cos': 'cos', r'\tan': 'tan',
    r'\arccos': 'arccos', r'\arcsin': 'arcsin', r'\arctan': 'arctan',
    r'\vec': '',
}


def latex_to_plain(text: str) -> str:
    """
    Перетворює LaTeX-конструкції, що використовуються у кроках розв'язання
    (планіметрія та аналітична геометрія), на плоский текст для reportlab,
    який LaTeX не рендерить. Коректно обробляє вкладені дужки (підрядкові
    індекси всередині \\frac/\\sqrt, \\frac всередині \\sqrt тощо).
    """
    if not text:
        return text

    s = text

    # Багаторядкові блоки: прибираємо обгортку, LaTeX-перенос "\\" -> реальний \n
    s = re.sub(r'\\begin\{[a-z]+\}', '', s)
    s = re.sub(r'\\end\{[a-z]+\}', '', s)
    s = s.replace('&', '')
    s = s.replace('\\\\', '\n')

    # Спершу розкриваємо під-/надрядкові дужки, щоб команди з аргументами
    # нижче коректно знаходили межі навіть при вкладеності
    s = _strip_script_braces(s)

    # "^\circ" -> "°" (без зайвого "^"); "\circ" саме по собі — теж на "°"
    s = re.sub(r'\^\s*\\circ', '°', s)
    s = s.replace(r'\circ', '°')

    s = _replace_command_with_args(s, r'\boxed', 1, lambda x: f'[ {x} ]')
    s = _replace_command_with_args(s, r'\frac', 2, lambda a, b: f'({a})/({b})')
    s = _replace_command_with_args(s, r'\sqrt', 1, lambda a: f'sqrt({a})')
    s = _replace_command_with_args(s, r'\text', 1, lambda a: a)

    for latex_cmd, plain in _SYMBOLS.items():
        s = s.replace(latex_cmd, plain)

    # Рештки одиночних (уже не вкладених) фігурних дужок, напр. від \vec{a} -> {a} -> a
    s = re.sub(r'\{([^{}]*)\}', r'\1', s)

    s = re.sub(r'[ \t]+', ' ', s)
    s = '\n'.join(line.strip() for line in s.split('\n'))
    return s.strip()