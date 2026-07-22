import math
from fractions import Fraction


def fmt_num(value: float) -> str:
    """Форматує число без зайвих нулів після коми (2.0 -> '2', 1.50 -> '1.5')."""
    if math.isclose(value, round(value), abs_tol=1e-9):
        return str(int(round(value)))
    return f"{value:.2f}".rstrip('0').rstrip('.')


def _leading_term(value: float, name: str = '') -> str:
    """Перший доданок у виразі: без знаку '+', з мінусом за потреби."""
    abs_str = fmt_num(abs(value))
    coef_str = '' if (name and math.isclose(abs(value), 1)) else abs_str
    sign = '-' if value < 0 else ''
    return f"{sign}{coef_str}{name}"


def _signed_term(value: float, name: str = '') -> str:
    """Доданок у середині виразу зі знаком, напр. ' + 3' або ' - y'."""
    abs_str = fmt_num(abs(value))
    coef_str = '' if (name and math.isclose(abs(value), 1)) else abs_str
    sign = '-' if value < 0 else '+'
    return f"{sign} {coef_str}{name}".strip()


def format_linear_expr(coef: float, var_name: str, const: float) -> str:
    """Формує вираз виду 'coef*var + const' (без знаку рівності), напр. '-3y + 6'."""
    pieces = [_leading_term(coef, var_name)]
    if not math.isclose(const, 0, abs_tol=1e-9):
        pieces.append(_signed_term(const))
    return " ".join(pieces)


def format_line_lhs(a: float, b: float, c: float, x_name: str = 'x', y_name: str = 'y') -> str:
    """Формує ліву частину рівняння прямої 'Ax + By + C' (без '= 0'), пропускаючи нульові доданки."""
    terms = [(a, x_name), (b, y_name), (c, '')]
    pieces = []
    for coef, name in terms:
        if math.isclose(coef, 0, abs_tol=1e-9):
            continue
        pieces.append(_leading_term(coef, name) if not pieces else _signed_term(coef, name))
    return " ".join(pieces) if pieces else "0"


def simplify_line_coefficients(a: float, b: float, c: float) -> tuple[float, float, float]:
    """
    Зводить рівняння Ax + By + C = 0 до найпростішого еквівалентного вигляду:
    цілі, взаємно прості коефіцієнти (де можливо), перший ненульовий — додатний.
    """
    fa = Fraction(a).limit_denominator(1000)
    fb = Fraction(b).limit_denominator(1000)
    fc = Fraction(c).limit_denominator(1000)

    denom = fa.denominator
    for fr in (fb, fc):
        denom = denom * fr.denominator // math.gcd(denom, fr.denominator)

    ia, ib, ic = int(fa * denom), int(fb * denom), int(fc * denom)

    g = math.gcd(math.gcd(abs(ia), abs(ib)), abs(ic))
    if g == 0:
        g = 1
    ia, ib, ic = ia // g, ib // g, ic // g

    for val in (ia, ib, ic):
        if val != 0:
            if val < 0:
                ia, ib, ic = -ia, -ib, -ic
            break

    return float(ia), float(ib), float(ic)