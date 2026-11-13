"""Call-sequence figures for the recursion practice PDF (light theme only).

Every figure is produced by actually running the recursion in Python and
recording each call, so the numbers in the pictures are computed, not typed;
each pNN() function also asserts the expected result.

Usage: python3 practice_figures.py OUT_DIR
Writes p01.svg ... p20.svg plus p20-block.svg.

Reusable for any recursion or algorithm figure:
  ladder(rungs, title, desc, output=None)
      U-shaped call ladder for linear recursion: calls down the left, answers
      up the right. Each rung is a dict with name, left (work before the
      call, blue), right (work after the call, green), lorder/rorder (print
      order badges) and ret (value returned; None for void functions).
      Raises ValueError if a rung's text would overflow, instead of drawing it.
  Trace       collects rungs while a real recursive function runs
  layout(), walk()
      tidy tree layout and pre-order walk for drawing call trees
  badge()     numbered circle used for print and traversal order
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post_figures import THEMES, doc, text, fig_hanoi  # noqa: E402

T = dict(THEMES["light"])
T.update(orange="#bc4c00", orangesoft="#fff1e5")

MONO_EM = 0.602  # advance width of one monospace character, in em


def mw(s, size):
    return len(s) * size * MONO_EM


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def badge(cx, cy, n, col):
    soft = {"accent": "accentsoft", "green": "greensoft", "orange": "orangesoft"}[col]
    return (f'<circle cx="{cx}" cy="{cy}" r="9.5" fill="{T[soft]}" stroke="{T[col]}" stroke-width="1.6"/>'
            + text(cx, cy + 4.3, str(n), T, cls="s b", size=11.5, fill=col, anchor="middle"))


# --------------------------------------------------------------------------
# Linear recursion: a U-shaped ladder, calls down the left, answers up the right
# --------------------------------------------------------------------------
def ladder(rungs, title, desc, output=None):
    """rungs: dicts with name, left, lorder, right, rorder, ret (None for void)."""
    W = 720
    n = len(rungs)
    top, rh, bh = 66, 72, 44
    step = min(28, 110 / max(1, n - 1))
    L = lambda k: 70 + step * k
    R = lambda k: W - 70 - step * k
    Y = lambda k: top + rh * k
    H = Y(n - 1) + bh + (62 if output else 26)
    valued = rungs[0].get("ret") is not None
    out = []

    b1, b2 = Y(0) + 4, Y(n - 1) + bh - 4
    mid = (b1 + b2) / 2
    out.append(f'<path d="M34,{b1} V{b2 - 12}" stroke="{T["accent"]}" stroke-width="3" stroke-linecap="round"/>')
    out.append(f'<path d="M27,{b2 - 14} L34,{b2} L41,{b2 - 14} z" fill="{T["accent"]}"/>')
    out.append(text(20, mid, "calls go down", T, cls="s b", size=13, fill="accent", anchor="middle",
                    extra=f'transform="rotate(-90 20 {mid})"'))
    out.append(f'<path d="M{W - 34},{b2} V{b1 + 12}" stroke="{T["green"]}" stroke-width="3" stroke-linecap="round"/>')
    out.append(f'<path d="M{W - 41},{b1 + 14} L{W - 34},{b1} L{W - 27},{b1 + 14} z" fill="{T["green"]}"/>')
    out.append(text(W - 20, mid, "answers come up" if valued else "calls return", T, cls="s b", size=13,
                    fill="green", anchor="middle", extra=f'transform="rotate(90 {W - 20} {mid})"'))

    for k, r in enumerate(rungs):
        x, y, w = L(k), Y(k), R(k) - L(k)
        base = k == n - 1
        fill, stroke = (T["greensoft"], T["green"]) if base else (T["box"], T["boxline"])
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{bh}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        if not base:
            out.append(f'<rect x="{x}" y="{y}" width="6" height="{bh}" rx="3" fill="{T["accent"]}"/>')
            out.append(f'<rect x="{x + w - 6}" y="{y}" width="6" height="{bh}" rx="3" fill="{T["green"]}"/>')
        name = r["name"]
        out.append(text(x + 20, y + 28, esc(name), T, cls="m b", size=14))
        lx = x + 20 + mw(name, 14)
        if r.get("left"):
            lx += 16
            if r.get("lorder"):
                out.append(badge(lx + 10, y + 23, r["lorder"], "accent"))
                lx += 24
            out.append(text(lx, y + 27.5, esc(r["left"]), T, size=13, fill="accent"))
            lx += mw(r["left"], 13)
        rx = x + w - 20
        if r.get("right"):
            out.append(text(rx, y + 28, esc(r["right"]), T, cls="m b", size=14, fill="green", anchor="end"))
            rx -= mw(r["right"], 14)
            if r.get("rorder"):
                out.append(badge(rx - 14, y + 23, r["rorder"], "green"))
                rx -= 28
        if lx + 14 > rx:
            raise ValueError(f"{title}: rung {k} overflows ({lx:.0f} > {rx:.0f}): {r}")

        if k < n - 1:
            g1, g2 = y + bh, Y(k + 1)
            dx = L(k + 1) + 30
            out.append(f'<path d="M{dx},{g1 + 3} V{g2 - 4}" stroke="{T["accent"]}" stroke-width="2.2" marker-end="url(#ah-a)"/>')
            ux = R(k + 1) - 30
            out.append(f'<path d="M{ux},{g2 - 3} V{g1 + 4}" stroke="{T["green"]}" stroke-width="2.2" marker-end="url(#ah-g)"/>')
            ret = rungs[k + 1].get("ret")
            if ret is not None:
                out.append(text(ux - 12, (g1 + g2) / 2 + 5, f"returns {esc(str(ret))}", T, cls="s b", size=12.5,
                                fill="green", anchor="end"))

    fx = R(0) - 30
    out.append(f'<path d="M{fx},{Y(0) - 3} V{16}" stroke="{T["green"]}" stroke-width="2.2" marker-end="url(#ah-g)"/>')
    final = f"returns {esc(str(rungs[0]['ret']))} to the caller" if valued else "back to the caller"
    out.append(text(fx - 12, 42, final, T, cls="s b", size=12.5, fill="green", anchor="end"))
    if output:
        out.append(text(70, H - 22, "output:", T, cls="s", size=13, fill="muted"))
        out.append(text(124, H - 22, esc(output), T, cls="m b", size=15))
    return doc(W, H, T, "\n".join(out), title, desc)


class Trace:
    """Collects rungs while a real recursion runs."""

    def __init__(self):
        self.rungs, self.prints = [], 0

    def call(self, name, **kw):
        r = dict(name=name, **kw)
        self.rungs.append(r)
        return r

    def printed(self):
        self.prints += 1
        return self.prints


# --------------------------------------------------------------------------
# The twenty problems, run for real
# --------------------------------------------------------------------------
def p01():
    a, tr, out = [69, 87, 45, 21, 47], Trace(), []

    def print_reverse(i, n):
        r = tr.call(f"print_reverse(i={i})")
        if i == n:
            r["right"] = "i == n, stop"
            return
        print_reverse(i + 1, n)
        out.append(a[i])
        r["right"], r["rorder"] = f"prints {a[i]}", tr.printed()

    print_reverse(0, len(a))
    assert out == [47, 21, 45, 87, 69]
    return ladder(tr.rungs, "Calls made by print_reverse", "Each call prints its element after the call below it returns, so 47 is printed first.",
                  output=" ".join(map(str, out)))


def p02():
    a, tr, out = [1, 5, 7, 8, 9], Trace(), []

    def print_ends(i, j):
        r = tr.call(f"print_ends(i={i}, j={j})")
        if i > j:
            r["right"] = "i > j, stop"
            return
        out.append((a[i], a[j]))
        r["left"], r["lorder"] = f"prints {a[i]} {a[j]}", tr.printed()
        print_ends(i + 1, j - 1)

    print_ends(0, len(a) - 1)
    assert out == [(1, 9), (5, 8), (7, 7)]
    return ladder(tr.rungs, "Calls made by print_ends", "Each call prints its pair before calling, so pairs come out from the ends inward.",
                  output=" / ".join(f"{x} {y}" for x, y in out))


def p03():
    tr, out = Trace(), []

    def print_series(i, n):
        r = tr.call(f"print_series(i={i})")
        if i == n:
            r["right"] = "i == n, stop"
            return
        s = "1" if i == 0 else " + x" if i == 1 else f" + x^{i}"
        out.append(s)
        r["left"], r["lorder"] = f'prints "{s}"', tr.printed()
        print_series(i + 1, n)

    print_series(0, 5)
    assert "".join(out) == "1 + x + x^2 + x^3 + x^4"
    return ladder(tr.rungs, "Calls made by print_series", "Each call prints one term before calling for the next.", output="".join(out))


def p04():
    line, tr, out = "helloo\n", Trace(), []
    pos = [0]

    def reverse_line():
        c = line[pos[0]]
        pos[0] += 1
        r = tr.call("reverse_line()")
        if c == "\n":
            r["right"] = "reads '\\n', stop"
            return
        r["left"] = f"reads '{c}'"
        reverse_line()
        out.append(c)
        r["right"], r["rorder"] = f"prints '{c}'", tr.printed()

    reverse_line()
    assert "".join(out) == "oolleh"
    return ladder(tr.rungs, "Calls made by reverse_line", "Each call reads one character on the way down and prints it on the way up.",
                  output="".join(out))


def p05():
    tr = Trace()

    def factorial(n):
        r = tr.call(f"factorial({n})")
        if n == 0:
            r["right"], r["ret"] = "base case: 1", 1
            return 1
        rest = factorial(n - 1)
        r["right"], r["ret"] = f"{n} × {rest} = {n * rest}", n * rest
        return n * rest

    assert factorial(5) == 120
    return ladder(tr.rungs, "Calls made by factorial(5)", "Each call multiplies n by the answer from below.")


def p07():
    tr = Trace()

    def series(x, n):
        r = tr.call(f"series({x}, {n})")
        if n == 0:
            r["right"], r["ret"] = "empty sum: 0", 0
            return 0
        rest = series(x, n - 1)
        v = 1 + x * rest
        r["right"], r["ret"] = f"1 + {x} × {rest} = {v}", v
        return v

    assert series(2, 5) == 31
    return ladder(tr.rungs, "Calls made by series(2, 5)", "Each call multiplies the answer from below by x and adds 1.")


def p08():
    a, tr = [7, 4, 9, 6, 2], Trace()

    def max_from(i, n):
        r = tr.call(f"max_from(i={i})")
        if i == n - 1:
            r["right"], r["ret"] = f"last one: {a[i]}", a[i]
            return a[i]
        r["left"] = f"a[{i}] = {a[i]}"
        rest = max_from(i + 1, n)
        best = max(a[i], rest)
        r["right"], r["ret"] = f"max({a[i]}, {rest}) = {best}", best
        return best

    assert max_from(0, len(a)) == 9
    return ladder(tr.rungs, "Calls made by max_from", "Each call compares its element with the largest of the rest.")


def p09():
    tr = Trace()

    def gcd(a, b):
        r = tr.call(f"gcd({a}, {b})")
        if b == 0:
            r["right"], r["ret"] = f"b == 0: {a}", a
            return a
        r["left"] = f"{a} % {b} = {a % b}"
        g = gcd(b, a % b)
        r["ret"] = g
        return g

    assert gcd(25, 8895) == 5
    return ladder(tr.rungs, "Calls made by gcd(25, 8895)", "Each call passes the answer from below straight up.")


def p10():
    tr = Trace()

    def my_strlen(s):
        r = tr.call(f'my_strlen("{s}")')
        if s == "":
            r["right"], r["ret"] = "empty: 0", 0
            return 0
        rest = my_strlen(s[1:])
        r["right"], r["ret"] = f"1 + {rest} = {1 + rest}", 1 + rest
        return 1 + rest

    assert my_strlen("abc") == 3
    return ladder(tr.rungs, 'Calls made by my_strlen("abc")', "Each call counts one character and adds the length of the rest.")


def p11():
    a, tr = [5, 8, 7, 9, 3], Trace()

    def top2(i, n):
        r = tr.call(f"top2(i={i})")
        if i == n - 1:
            r["right"], r["ret"] = f"last one: {{{a[i]}, -∞}}", f"{{{a[i]}, -∞}}"
            return (a[i], float("-inf"))
        r["left"] = f"a[{i}] = {a[i]}"
        first, second = top2(i + 1, n)
        if a[i] > first:
            first, second, why = a[i], first, "new largest"
        elif a[i] > second:
            second, why = a[i], "new second"
        else:
            why = "no change"
        v = f"{{{first}, {second}}}"
        r["right"], r["ret"] = f"{why}: {v}", v
        return (first, second)

    assert top2(0, len(a)) == (9, 8)
    return ladder(tr.rungs, "Calls made by top2", "Each call fits its element into the top two of the rest.")


def p12():
    tr = Trace()

    def is_prime(n, d):
        r = tr.call(f"is_prime({n}, {d})")
        if n < 2:
            r["right"], r["ret"] = "n < 2: 0", 0
            return 0
        if d * d > n:
            r["right"], r["ret"] = f"{d}×{d} > {n}: 1", 1
            return 1
        if n % d == 0:
            r["right"], r["ret"] = f"{n} % {d} == 0: 0", 0
            return 0
        r["left"] = f"{n} % {d} = {n % d}"
        v = is_prime(n, d + 1)
        r["ret"] = v
        return v

    assert is_prime(49, 2) == 0
    return ladder(tr.rungs, "Calls made by is_prime(49, 2)", "Each call tries one divisor; 7 divides 49.")


def p13():
    tr = Trace()

    def lcm(a, b, m):
        r = tr.call(f"lcm({a}, {b}, {m})")
        if m % b == 0:
            r["right"], r["ret"] = f"{m} % {b} == 0: {m}", m
            return m
        r["left"] = f"{m} % {b} = {m % b}"
        v = lcm(a, b, m + a)
        r["ret"] = v
        return v

    assert lcm(4, 6, 4) == 12
    return ladder(tr.rungs, "Calls made by lcm(4, 6, 4)", "m walks through the multiples of 4 until one is divisible by 6.")


def p14():
    tr = Trace()

    def reverse_int(n, acc):
        r = tr.call(f"reverse_int({n}, {acc})")
        if n == 0:
            r["right"], r["ret"] = f"n == 0: {acc}", acc
            return acc
        r["left"] = f"acc → {acc * 10 + n % 10}"
        v = reverse_int(n // 10, acc * 10 + n % 10)
        r["ret"] = v
        return v

    assert reverse_int(123405, 0) == 504321
    return ladder(tr.rungs, "Calls made by reverse_int(123405, 0)", "The answer is built in acc on the way down and passed back up unchanged.")


def p15():
    a, tr = [1, 54, 88, 6, 55, 7], Trace()

    def remove_odds(i, j, n):
        r = tr.call(f"remove_odds(i={i}, j={j})")
        if i == n:
            r["right"], r["ret"] = f"i == n: {j}", j
            return j
        if a[i] % 2 == 0:
            r["left"] = f"a[{j}] = {a[i]}"
            a[j] = a[i]
            j += 1
        else:
            r["left"] = f"{a[i]} is odd, skip"
        v = remove_odds(i + 1, j, n)
        r["ret"] = v
        return v

    n = remove_odds(0, 0, len(a))
    assert a[:n] == [54, 88, 6]
    return ladder(tr.rungs, "Calls made by remove_odds", "Even numbers are copied down to position j; j is the new length.",
                  output=" ".join(map(str, a[:n])))


def p16():
    a, tr = [2, 9, 4, 7, 6], Trace()

    def find(i, n, v):
        r = tr.call(f"find(i={i})")
        if i == n:
            r["right"], r["ret"] = "i == n: -1", -1
            return -1
        if a[i] == v:
            r["right"], r["ret"] = f"a[{i}] == {v}: {i}", i
            return i
        r["left"] = f"a[{i}] = {a[i]} ≠ {v}"
        res = find(i + 1, n, v)
        r["ret"] = res
        return res

    assert find(0, len(a), 5) == -1
    return ladder(tr.rungs, "Calls made by find, looking for 5", "Every element is checked and none matches, so -1 comes back.")


def p17():
    a, tr = [1, 2, 3, 4, 5], Trace()

    def binary_search(lo, hi, v):
        r = tr.call(f"binary_search({lo}, {hi})")
        if lo > hi:
            r["right"], r["ret"] = "lo > hi: -1", -1
            return -1
        mid = lo + (hi - lo) // 2
        if a[mid] < v:
            r["left"] = f"a[{mid}] = {a[mid]} < {v}: go right"
            res = binary_search(mid + 1, hi, v)
        elif a[mid] > v:
            r["left"] = f"a[{mid}] = {a[mid]} > {v}: go left"
            res = binary_search(lo, mid - 1, v)
        else:
            r["right"], r["ret"] = f"a[{mid}] == {v}: {mid}", mid
            return mid
        r["ret"] = res
        return res

    assert binary_search(0, 4, -5) == -1
    return ladder(tr.rungs, "Calls made by binary_search, looking for -5", "Each call halves the range until it is empty.")


def p18():
    s, tr = "pop, pop", Trace()

    def is_palindrome(i, j):
        r = tr.call(f"is_palindrome({i}, {j})")
        if i >= j:
            r["right"], r["ret"] = "i >= j: 1", 1
            return 1
        if not s[i].isalnum():
            r["left"] = f"skip '{s[i]}' at i"
            v = is_palindrome(i + 1, j)
        elif not s[j].isalnum():
            r["left"] = f"skip '{s[j]}' at j"
            v = is_palindrome(i, j - 1)
        elif s[i] != s[j]:
            r["right"], r["ret"] = f"'{s[i]}' != '{s[j]}': 0", 0
            return 0
        else:
            r["left"] = f"'{s[i]}' == '{s[j]}'"
            v = is_palindrome(i + 1, j - 1)
        r["ret"] = v
        return v

    assert is_palindrome(0, len(s) - 1) == 1
    return ladder(tr.rungs, 'Calls made by is_palindrome on "pop, pop"', "Each call checks the outer pair and moves inward, skipping punctuation.")


# --------------------------------------------------------------------------
# Branching recursion: call trees
# --------------------------------------------------------------------------
def layout(node, depth=0, slot=None):
    """Tidy layout: leaves take consecutive slots, parents sit over their children."""
    if slot is None:
        slot = [0]
    node["depth"] = depth
    if not node["kids"]:
        node["slot"] = slot[0]
        slot[0] += 1
    else:
        for k in node["kids"]:
            layout(k, depth + 1, slot)
        node["slot"] = sum(k["slot"] for k in node["kids"]) / len(node["kids"])
    return slot[0]


def walk(node):
    yield node
    for k in node["kids"]:
        yield from walk(k)


def p06():
    def fib(n):
        node = {"n": n, "kids": []}
        if n <= 2:
            node["val"] = 1
        else:
            node["kids"] = [fib(n - 1), fib(n - 2)]
            node["val"] = node["kids"][0]["val"] + node["kids"][1]["val"]
        return node

    root = fib(5)
    assert root["val"] == 5
    leaves = layout(root)
    W, x0, sw, dy, top, bw, bh = 720, 100, 130, 82, 24, 116, 36
    X = lambda nd: x0 + nd["slot"] * sw
    Yn = lambda nd: top + nd["depth"] * dy
    depth = max(nd["depth"] for nd in walk(root))
    H = top + depth * dy + bh + 52
    out = []
    for nd in walk(root):
        for k in nd["kids"]:
            out.append(f'<line x1="{X(nd)}" y1="{Yn(nd) + bh}" x2="{X(k)}" y2="{Yn(k)}" stroke="{T["line"]}" stroke-width="1.8"/>')
            out.append(text((X(nd) + X(k)) / 2 + (10 if X(k) > X(nd) else -10), (Yn(nd) + bh + Yn(k)) / 2 + 4,
                            f"↑ {k['val']}", T, cls="m b", size=12, fill="green", anchor="start" if X(k) > X(nd) else "end"))
    for nd in walk(root):
        base = not nd["kids"]
        fill, stroke = (T["greensoft"], T["green"]) if base else (T["box"], T["boxline"])
        out.append(f'<rect x="{X(nd) - bw / 2}" y="{Yn(nd)}" width="{bw}" height="{bh}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        out.append(text(X(nd), Yn(nd) + 23, f'fib({nd["n"]}) = <tspan fill="{T["green"]}">{nd["val"]}</tspan>',
                        T, cls="m b", size=14, anchor="middle"))
    out.append(f'<rect x="30" y="{H - 34}" width="18" height="14" rx="4" fill="{T["greensoft"]}" stroke="{T["green"]}" stroke-width="1.6"/>')
    out.append(text(56, H - 22, "base case, n ≤ 2: returns 1", T, cls="s", size=13, fill="muted"))
    out.append(text(W - 30, H - 22, "↑ value returned to the caller", T, cls="s", size=13, fill="green", anchor="end"))
    return doc(W, H, T, "\n".join(out), "Calls made by fib(5)",
               "The call tree of fib(5). Each call returns the sum of its two children's values; fib(3) is computed twice and fib(2) three times.")


def p19():
    def fib(n):
        return {"n": n, "kids": [] if n <= 2 else [fib(n - 1), fib(n - 2)]}

    root = fib(5)
    layout(root)
    pre, ino, post = [], [], []

    def visit(nd):
        if not nd["kids"]:
            for seq in (pre, ino, post):
                seq.append(nd)
            return
        pre.append(nd)
        visit(nd["kids"][0])
        ino.append(nd)
        visit(nd["kids"][1])
        post.append(nd)

    visit(root)
    assert [nd["n"] for nd in pre] == [5, 4, 3, 2, 1, 2, 3, 2, 1]
    assert [nd["n"] for nd in ino] == [2, 3, 1, 4, 2, 5, 2, 3, 1]
    assert [nd["n"] for nd in post] == [2, 1, 3, 2, 4, 2, 1, 3, 5]
    W, x0, sw, dy, top, r = 720, 110, 125, 76, 34, 19
    X = lambda nd: x0 + nd["slot"] * sw
    Yn = lambda nd: top + nd["depth"] * dy
    depth = max(nd["depth"] for nd in walk(root))
    H = top + depth * dy + r + 78
    out = []
    for nd in walk(root):
        for k in nd["kids"]:
            out.append(f'<line x1="{X(nd)}" y1="{Yn(nd)}" x2="{X(k)}" y2="{Yn(k)}" stroke="{T["line"]}" stroke-width="1.8"/>')
    for nd in walk(root):
        leaf = not nd["kids"]
        stroke = T["green"] if leaf else T["ink"]
        out.append(f'<circle cx="{X(nd)}" cy="{Yn(nd)}" r="{r}" fill="{T["focus"]}" stroke="{stroke}" stroke-width="2"/>')
        out.append(text(X(nd), Yn(nd) + 5.5, str(nd["n"]), T, cls="m b", size=15, fill="green" if leaf else "ink", anchor="middle"))
    for seq, col, dx, dyy in ((pre, "accent", -31, -14), (ino, "orange", 0, 33), (post, "green", 31, -14)):
        for i, nd in enumerate(seq, 1):
            out.append(badge(X(nd) + dx, Yn(nd) + dyy, i, col))
    ly = H - 30
    for i, (col, label) in enumerate((("accent", "preorder: before the calls"),
                                      ("orange", "inorder: between the calls"),
                                      ("green", "postorder: after the calls"))):
        lx = 40 + i * 225
        out.append(badge(lx, ly - 4, "#", col))
        out.append(text(lx + 16, ly + 1, label, T, cls="s", size=13, fill=col))
    return doc(W, H, T, "\n".join(out), "The three print orders of fib(5)",
               "The call tree of fib(5). Each node carries three numbered badges: blue on the left for the preorder position, "
               "orange underneath for inorder, green on the right for postorder.")


def p20_tree():
    moves = []

    def hanoi(n, frm, via, to):
        node = {"label": f"hanoi({n}, {frm}→{to})", "kids": []}
        if n == 1:
            moves.append((frm, to))
            node["move"] = (len(moves), frm, to)
            return node
        left = hanoi(n - 1, frm, to, via)
        moves.append((frm, to))
        node["move"] = (len(moves), frm, to)
        right = hanoi(n - 1, via, frm, to)
        node["kids"] = [left, right]
        return node

    root = hanoi(3, "a", "b", "c")
    assert moves == [("a", "c"), ("a", "b"), ("c", "b"), ("a", "c"), ("b", "a"), ("b", "c"), ("a", "c")]
    layout(root)
    W, x0, sw, dy, top, bw, bh = 720, 110, 167, 98, 24, 140, 54
    X = lambda nd: x0 + nd["slot"] * sw
    Yn = lambda nd: top + nd["depth"] * dy
    depth = max(nd["depth"] for nd in walk(root))
    H = top + depth * dy + bh + 46
    out = []
    for nd in walk(root):
        for k in nd["kids"]:
            out.append(f'<line x1="{X(nd)}" y1="{Yn(nd) + bh}" x2="{X(k)}" y2="{Yn(k)}" stroke="{T["line"]}" stroke-width="1.8"/>')
    for nd in walk(root):
        leaf = not nd["kids"]
        fill, stroke = (T["greensoft"], T["green"]) if leaf else (T["box"], T["boxline"])
        x, y = X(nd) - bw / 2, Yn(nd)
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        out.append(text(X(nd), y + 22, nd["label"], T, cls="m b", size=13.5, anchor="middle"))
        order, frm, to = nd["move"]
        out.append(badge(X(nd) - 30, y + 39, order, "green"))
        out.append(text(X(nd) - 16, y + 43.5, f"{frm} → {to}", T, cls="m b", size=13.5, fill="green"))
    out.append(text(30, H - 18, "Badges number the moves in the order they are printed. Calls with n = 0 are not drawn.",
                    T, cls="s", size=12.5, fill="muted"))
    return doc(W, H, T, "\n".join(out), "Calls made by hanoi(3, a, b, c)",
               "The call tree of hanoi(3) moving from a to c. Each call prints its move between its two calls, so the seven moves "
               "come out in inorder: a→c, a→b, c→b, a→c, b→a, b→c, a→c.")


FIGS = {
    "p01": p01, "p02": p02, "p03": p03, "p04": p04, "p05": p05, "p06": p06, "p07": p07,
    "p08": p08, "p09": p09, "p10": p10, "p11": p11, "p12": p12, "p13": p13, "p14": p14,
    "p15": p15, "p16": p16, "p17": p17, "p18": p18, "p19": p19, "p20": p20_tree,
    "p20-block": lambda: fig_hanoi(T),
}

if __name__ == "__main__":
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    for name, fn in FIGS.items():
        with open(os.path.join(out_dir, f"{name}.svg"), "w", encoding="utf-8") as f:
            f.write(fn())
    print(f"wrote {len(FIGS)} figures to {out_dir}")
