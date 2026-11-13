"""Randomized check of the 20 practice-PDF solutions against Python references.

Usage: python3 fuzz_solutions.py [CASES_PER_PROBLEM]   (default 150)

Compiles each solution with the same main() wrappers as check_solutions.py,
feeds it random inputs, and compares the output with a plain Python
reference: math.gcd/factorial, trial division, sorted(), list.index, string
reversal, and so on. Tower of Hanoi output is replayed move by move to check
that every move is legal and all disks end on peg c in 2^n - 1 moves.
The seed is fixed, so a run is reproducible.
"""
import math
import os
import random
import re
import string
import subprocess
import sys
import tempfile

tools = os.path.dirname(os.path.abspath(__file__))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
sys.path.insert(0, tools)
from check_solutions import MAINS, PRELUDE, normalize  # noqa: E402

random.seed(20261114)
blocks = re.findall(r"^```c\n(.*?)^```", open(os.path.join(tools, "practice_source.md")).read(), flags=re.S | re.M)


def ints(lo=-100, hi=100, n=None):
    return [random.randint(lo, hi) for _ in range(n if n is not None else random.randint(1, 20))]


def j(a):
    return " ".join(map(str, a))


def series_str(n):
    return "".join("1" if i == 0 else " + x" if i == 1 else f" + x^{i}" for i in range(n))


def fib(n):
    a, b = 1, 1
    for _ in range(n - 2):
        a, b = b, a + b
    return 1 if n <= 2 else b


def isprime(n):
    return n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))


def orders(n):
    pre, ino, post = [], [], []

    def go(k):
        if k <= 2:
            pre.append(k); ino.append(k); post.append(k)
            return
        pre.append(k); go(k - 1); ino.append(k); go(k - 2); post.append(k)
    go(n)
    return f"Preorder:  {j(pre)}\nInorder:   {j(ino)}\nPostorder: {j(post)}"


def hanoi_ok(n, out):
    pegs = {"a": list(range(n, 0, -1)), "b": [], "c": []}
    moves = [m.split(" -> ") for m in out.strip().splitlines()] if n else []
    for frm, to in moves:
        if not pegs[frm] or (pegs[to] and pegs[to][-1] < pegs[frm][-1]):
            return False
        pegs[to].append(pegs[frm].pop())
    return len(moves) == 2 ** n - 1 and pegs["c"] == list(range(n, 0, -1))


def rand_line():
    chars = string.ascii_letters + string.digits + " ,.'!?-"
    return "".join(random.choice(chars) for _ in range(random.randint(0, 30)))


def pal_line():
    if random.random() < 0.5:
        return rand_line()
    core = "".join(random.choice("abcXY12") for _ in range(random.randint(0, 6)))
    s = core + random.choice(["", "z", "7"]) + core[::-1]
    return "".join(c + (random.choice(" ,'") if random.random() < 0.3 else "") for c in s)


def gen(i):
    """Return (input text, expected output, or a checker function)."""
    if i == 1:
        a = ints(); return j(a), j(a[::-1])
    if i == 2:
        a = ints(); n = len(a); return j(a), "\n".join(f"{a[k]} {a[n - 1 - k]}" for k in range((n + 1) // 2))
    if i == 3:
        n = random.randint(1, 12); return str(n), series_str(n)
    if i == 4:
        s = rand_line(); return s, s[::-1]
    if i == 5:
        n = random.randint(0, 20); return str(n), str(math.factorial(n))
    if i == 6:
        n = random.randint(1, 27); return str(n), str(fib(n))
    if i == 7:
        x, n = random.randint(-5, 5), random.randint(0, 12); return f"{x} {n}", str(sum(x ** k for k in range(n)))
    if i == 8:
        a = ints(); return j(a), str(max(a))
    if i == 9:
        a, b = random.randint(0, 10 ** 6), random.randint(0, 10 ** 6); return f"{a} {b}", str(math.gcd(a, b))
    if i == 10:
        s = "".join(random.choice("abc") for _ in range(random.randint(1, 8)))
        t = "".join(random.choice("abc") for _ in range(random.randint(1, 8)))
        c = "negative" if s < t else "positive" if s > t else "zero"
        return f"{s}\n{t}", f"length:  {len(s)}\ncopy:    {s}\nappend:  {s + t}\ncompare: {c}"
    if i == 11:
        a = ints(-20, 20, random.randint(2, 20)); return j(a), str(sorted(a, reverse=True)[1])
    if i == 12:
        a = [random.choice([random.randint(-5, 200), random.randint(2, 10 ** 6), 999983, 2147483647])
             for _ in range(random.randint(1, 6))]
        return "\n".join(map(str, a)), "\n".join("prime" if isprime(v) else "not prime" for v in a)
    if i == 13:
        a, b = random.randint(1, 300), random.randint(1, 300); return f"{a} {b}", str(a * b // math.gcd(a, b))
    if i == 14:
        n = random.randint(0, 999999999); return str(n), str(int(str(n)[::-1]))
    if i == 15:
        a = ints(); return j(a), j([v for v in a if v % 2 == 0])
    if i == 16:
        a = ints(0, 15); q = ints(0, 18, random.randint(1, 6))
        return f"{j(a)}\n{j(q)}", "\n".join(str(a.index(v)) if v in a else "-1" for v in q)
    if i == 17:
        a = sorted(random.sample(range(-50, 50), random.randint(1, 20))); q = ints(-55, 55, random.randint(1, 6))
        return f"{j(a)}\n{j(q)}", "\n".join(str(a.index(v)) if v in a else "-1" for v in q)
    if i == 18:
        lines = [pal_line() for _ in range(random.randint(1, 4))]
        exp = []
        for s in lines:
            f = [c for c in s if c.isalnum()]
            exp.append("palindrome" if f == f[::-1] else "not palindrome")
        return "\n".join(lines), "\n".join(exp)
    if i == 19:
        n = random.randint(1, 10); return str(n), orders(n)
    if i == 20:
        n = random.randint(0, 10); return str(n), (lambda out, n=n: hanoi_ok(n, out))


with tempfile.TemporaryDirectory() as tmp:
    total_fail = 0
    for i, (code, main_c) in enumerate(zip(blocks, MAINS), 1):
        src, exe = os.path.join(tmp, f"p{i}.c"), os.path.join(tmp, f"p{i}")
        open(src, "w").write(PRELUDE + code + "\n" + main_c + "\n")
        subprocess.run(["gcc", "-std=c11", "-O2", "-o", exe, src], check=True)
        fails = 0
        for _ in range(N):
            inp, exp = gen(i)
            out = subprocess.run([exe], input=inp + "\n", capture_output=True, text=True, timeout=20).stdout
            ok = exp(out) if callable(exp) else normalize(out) == normalize(exp)
            if not ok:
                fails += 1
                if fails <= 2:
                    print(f"  p{i} FAIL input={inp!r}\n    expected={exp if not callable(exp) else 'legal moves'!r}\n    got={out!r}")
        total_fail += fails
        print(f"p{i:02}: {N - fails}/{N} random cases pass")
    print("ALL PASS" if total_fail == 0 else f"{total_fail} failures")
