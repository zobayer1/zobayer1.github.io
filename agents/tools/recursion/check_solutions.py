"""Verify the practice PDF's solutions against its own Input/Output boxes.

For each of the 20 problems this takes the C code block exactly as the PDF
prints it (from practice_source.md), wraps it in a small main() that reads the
problem's Input box from stdin, compiles it with strict warnings, runs it, and
compares stdout with the problem's Output box (trailing spaces ignored).

The Input/Output text comes from PROBLEMS in build_practice_pdf.py, so a
change to either the code or the printed samples is caught here.

Usage: python3 check_solutions.py [practice_source.md]
Exit status is non-zero if anything fails to compile or match.
"""

import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_practice_pdf import PROBLEMS  # noqa: E402

PRELUDE = "#include <ctype.h>\n#include <limits.h>\n#include <stdio.h>\n#include <string.h>\n\n"

READ_INTS = """
static int read_ints(int *a) {
    int n = 0;
    while (scanf("%d", &a[n]) == 1) n++;
    return n;
}
"""

PARSE_INTS = """
static int parse_ints(const char *s, int *a) {
    int n = 0, k;
    while (sscanf(s, "%d%n", &a[n], &k) == 1) { n++; s += k; }
    return n;
}
"""

# One main() per problem, in PDF order. Each reads the Input box format.
MAINS = [
    READ_INTS + 'int main(void) { int a[64], n = read_ints(a); print_reverse(a, 0, n); printf("\\n"); return 0; }',
    READ_INTS + "int main(void) { int a[64], n = read_ints(a); print_ends(a, 0, n - 1); return 0; }",
    'int main(void) { int n; if (scanf("%d", &n) != 1) return 1; print_series(0, n); printf("\\n"); return 0; }',
    'int main(void) { reverse_line(); printf("\\n"); return 0; }',
    'int main(void) { int n; if (scanf("%d", &n) != 1) return 1; printf("%lld\\n", factorial(n)); return 0; }',
    'int main(void) { int n; if (scanf("%d", &n) != 1) return 1; printf("%lld\\n", fib(n)); return 0; }',
    'int main(void) { long long x; int n; if (scanf("%lld %d", &x, &n) != 2) return 1; printf("%lld\\n", series(x, n)); return 0; }',
    READ_INTS + 'int main(void) { int a[64], n = read_ints(a); printf("%d\\n", max_from(a, 0, n)); return 0; }',
    'int main(void) { int a, b; if (scanf("%d %d", &a, &b) != 2) return 1; printf("%d\\n", gcd(a, b)); return 0; }',
    """int main(void) {
    char s[64], t[64], buf[128];
    if (scanf("%63s %63s", s, t) != 2) return 1;
    printf("length:  %d\\n", my_strlen(s));
    my_strcpy(buf, s);
    printf("copy:    %s\\n", buf);
    my_strcat(buf, t);
    printf("append:  %s\\n", buf);
    int c = my_strcmp(s, t);
    printf("compare: %s\\n", c < 0 ? "negative" : c > 0 ? "positive" : "zero");
    return 0;
}""",
    READ_INTS + 'int main(void) { int a[64], n = read_ints(a); printf("%d\\n", top2(a, 0, n).second); return 0; }',
    'int main(void) { int n; while (scanf("%d", &n) == 1) printf("%s\\n", is_prime(n, 2) ? "prime" : "not prime"); return 0; }',
    'int main(void) { long long a, b; if (scanf("%lld %lld", &a, &b) != 2) return 1; printf("%lld\\n", lcm(a, b, a)); return 0; }',
    'int main(void) { int n; if (scanf("%d", &n) != 1) return 1; printf("%d\\n", reverse_int(n, 0)); return 0; }',
    READ_INTS + """int main(void) {
    int a[64], n = read_ints(a);
    n = remove_odds(a, 0, 0, n);
    for (int i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\\n");
    return 0;
}""",
    PARSE_INTS + """int main(void) {
    char line[256];
    int a[64], q[64], n, m;
    if (!fgets(line, sizeof line, stdin)) return 1;
    n = parse_ints(line, a);
    if (!fgets(line, sizeof line, stdin)) return 1;
    m = parse_ints(line, q);
    for (int i = 0; i < m; i++) printf("%d\\n", find(a, 0, n, q[i]));
    return 0;
}""",
    PARSE_INTS + """int main(void) {
    char line[256];
    int a[64], q[64], n, m;
    if (!fgets(line, sizeof line, stdin)) return 1;
    n = parse_ints(line, a);
    if (!fgets(line, sizeof line, stdin)) return 1;
    m = parse_ints(line, q);
    for (int i = 0; i < m; i++) printf("%d\\n", binary_search(a, 0, n - 1, q[i]));
    return 0;
}""",
    """int main(void) {
    char s[256];
    while (fgets(s, sizeof s, stdin))
        printf("%s\\n", is_palindrome(s, 0, (int)strlen(s) - 1) ? "palindrome" : "not palindrome");
    return 0;
}""",
    """int main(void) {
    int n;
    if (scanf("%d", &n) != 1) return 1;
    printf("Preorder: ");
    preorder(n);
    printf("\\nInorder:  ");
    inorder(n);
    printf("\\nPostorder:");
    postorder(n);
    printf("\\n");
    return 0;
}""",
    "int main(void) { int n; if (scanf(\"%d\", &n) != 1) return 1; hanoi(n, 'a', 'b', 'c'); return 0; }",
]


def normalize(s):
    return "\n".join(line.rstrip() for line in s.strip("\n").splitlines())


def main(source_md):
    blocks = re.findall(r"^```c\n(.*?)^```", open(source_md, encoding="utf-8").read(), flags=re.S | re.M)
    assert len(blocks) == len(PROBLEMS) == len(MAINS) == 20, (len(blocks), len(PROBLEMS), len(MAINS))
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (code, prob, main_c) in enumerate(zip(blocks, PROBLEMS, MAINS), 1):
            title, inp, expected = prob[1], prob[3], prob[4]
            src, exe = os.path.join(tmp, f"p{i:02}.c"), os.path.join(tmp, f"p{i:02}")
            with open(src, "w", encoding="utf-8") as f:
                f.write(PRELUDE + code + "\n" + main_c + "\n")
            cc = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-pedantic", "-Werror", "-O0", "-o", exe, src],
                                capture_output=True, text=True)
            if cc.returncode != 0:
                failures += 1
                print(f"FAIL {i:2} {title}: does not compile cleanly\n{cc.stderr}")
                continue
            run = subprocess.run([exe], input=inp + "\n", capture_output=True, text=True, timeout=10)
            got = normalize(run.stdout)
            if run.returncode != 0 or got != normalize(expected):
                failures += 1
                print(f"FAIL {i:2} {title}\n  expected: {normalize(expected)!r}\n  got:      {got!r}")
            else:
                print(f"ok   {i:2} {title}")
    print(f"\n{20 - failures}/20 solutions match their Input/Output boxes")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "practice_source.md")))
