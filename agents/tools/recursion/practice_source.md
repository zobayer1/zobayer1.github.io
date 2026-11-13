---
layout: post
title:  "Don't Fear Recursion: 20 Practice Problems"
date:   2026-11-14 00:20:00 +0600
categories: [Algorithms]
tags: [Recursion, Practice, Beginners, C]
math: true
---
Twenty small problems to build the two habits from [Don't Fear Recursion](/posts/dont-fear-recursion/): **trust the function** when you write it, **focus on one step** when you trace it. They are grouped by the idea they exercise, and get harder within each group.

> **Rules:** no loops and no global variables inside the recursive function. Whatever a step needs travels in its parameters or comes back in its return value. That's the whole point of the exercise.
{: .prompt-info }

> **Try before you peek.** Each solution shows only the recursive function and how to call it. Reading input and printing output is up to you. The code is C, but the ideas carry over to any language.
{: .prompt-tip }

## **On the way down, on the way up**

Work before the recursive call runs in calling order; work after it runs in reverse.

### 1. Print an array in reverse

`69 87 45 21 47` → `47 21 45 87 69`

<details markdown="1">
<summary>Solution</summary>

```c
// call: print_reverse(a, 0, n)
void print_reverse(const int *a, int i, int n) {
    if (i == n) return;
    print_reverse(a, i + 1, n);
    printf("%d ", a[i]);
}
```

Move the `printf` above the call and it prints in the original order.

</details>

### 2. Print from both ends

Print the first and last elements, then the second and second-to-last, and so on, until they meet in the middle.

`1 5 7 8 9` →

```text
1 9
5 8
7 7
```

<details markdown="1">
<summary>Solution</summary>

```c
// call: print_ends(a, 0, n - 1)
void print_ends(const int *a, int i, int j) {
    if (i > j) return;
    printf("%d %d\n", a[i], a[j]);
    print_ends(a, i + 1, j - 1);
}
```

Swap the last two lines to print from the middle outwards.

</details>

### 3. Print a series

Given $n$, print $1 + x + x^2 + \dots + x^{n-1}$.

`5` → `1 + x + x^2 + x^3 + x^4`

<details markdown="1">
<summary>Solution</summary>

```c
// call: print_series(0, n)
void print_series(int i, int n) {
    if (i == n) return;
    if (i == 0) printf("1");
    else if (i == 1) printf(" + x");
    else printf(" + x^%d", i);
    print_series(i + 1, n);
}
```

Try next: print it highest power first, `x^4 + x^3 + x^2 + x + 1`.

</details>

### 4. Reverse a line without an array

Read a line and print it backwards. No arrays and no strings, only `getchar()` and `putchar()`.

`helloo` → `oolleh`

<details markdown="1">
<summary>Solution</summary>

```c
void reverse_line(void) {
    int c = getchar();
    if (c == '\n' || c == EOF) return;
    reverse_line();
    putchar(c);
}
```

Every paused call holds one character in its own `c`. The call stack *is* the array.

</details>

## **Trust the smaller answer**

Promise what the function returns, answer the case you already know, and build everything else from a smaller answer.

### 5. Factorial

`5` → `120`

<details markdown="1">
<summary>Solution</summary>

```c
long long factorial(int n) {
    if (n == 0) return 1;
    return n * factorial(n - 1);
}
```

`long long` holds up to $20!$. Try next: do the multiplication *before* the call, carrying the product so far in a second parameter.

</details>

### 6. Fibonacci

The $n$'th Fibonacci number, where the first two are both 1.

`6` → `8`

<details markdown="1">
<summary>Solution</summary>

```c
long long fib(int n) {
    if (n <= 2) return 1;
    return fib(n - 1) + fib(n - 2);
}
```

Correct, but slow for large $n$. See [Recursion can be expensive](/posts/dont-fear-recursion/#recursion-can-be-expensive).

</details>

### 7. Sum of a series

Given $x$ and $n$, compute $1 + x + x^2 + \dots + x^{n-1}$.

`2 5` → `31`

<details markdown="1">
<summary>Solution</summary>

Factor out an $x$: $1 + x(1 + x + \dots + x^{n-2})$. The bracket is the same problem for $n - 1$.

```c
// promise: series(x, n) returns 1 + x + ... + x^(n-1)
long long series(long long x, int n) {
    if (n == 0) return 0;
    return 1 + x * series(x, n - 1);
}
```

No `pow()` needed.

</details>

### 8. Maximum of an array

`7 4 9 6 2` → `9`

<details markdown="1">
<summary>Solution</summary>

```c
// promise: max_from(a, i, n) returns the largest of a[i..n-1]
int max_from(const int *a, int i, int n) {
    if (i == n - 1) return a[i];
    int rest = max_from(a, i + 1, n);
    return a[i] > rest ? a[i] : rest;
}
```

Try next: the minimum.

</details>

### 9. Greatest common divisor

`25 8895` → `5`

<details markdown="1">
<summary>Solution</summary>

```c
int gcd(int a, int b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}
```

Euclid's algorithm: $\gcd(a, b) = \gcd(b, a \bmod b)$. The depth is only $O(\log \min(a, b))$, the safe kind.

</details>

### 10. String functions

Write your own `strlen`, `strcpy`, `strcat` and `strcmp`. Test them against the library versions.

<details markdown="1">
<summary>Solution</summary>

```c
int my_strlen(const char *s) {
    if (*s == '\0') return 0;
    return 1 + my_strlen(s + 1);
}

void my_strcpy(char *dst, const char *src) {
    *dst = *src;
    if (*src != '\0') my_strcpy(dst + 1, src + 1);
}

void my_strcat(char *dst, const char *src) {
    if (*dst == '\0') my_strcpy(dst, src);
    else my_strcat(dst + 1, src);
}

int my_strcmp(const char *a, const char *b) {
    if (*a != *b || *a == '\0') return (unsigned char)*a - (unsigned char)*b;
    return my_strcmp(a + 1, b + 1);
}
```

`s + 1` is the rest of the string, the smaller problem. The library `strcpy` and `strcat` also return `dst`, which is left out here.

</details>

### 11. Second maximum

`5 8 7 9 3` → `8`

Hint: the second maximum of the rest isn't enough on its own. Promise more.

<details markdown="1">
<summary>Solution</summary>

```c
#include <limits.h>

typedef struct { int first, second; } Top2;

// promise: top2(a, i, n) returns the two largest of a[i..n-1]
Top2 top2(const int *a, int i, int n) {
    if (i == n - 1) return (Top2){ a[i], INT_MIN };
    Top2 t = top2(a, i + 1, n);
    if (a[i] > t.first) {
        t.second = t.first;
        t.first = a[i];
    } else if (a[i] > t.second) {
        t.second = a[i];
    }
    return t;
}
```

Call `top2(a, 0, n).second`. A C function can return a struct, which is how one call hands back two answers without globals.

</details>

## **Carry it in the parameters**

Sometimes there's no smaller answer to trust, only progress to make. Then the parameters carry the state of the work, like a loop counter.

### 12. Prime test

`49` → `not prime`, `999983` → `prime`, `1` → `not prime`

<details markdown="1">
<summary>Solution</summary>

```c
// call: is_prime(n, 2)
int is_prime(int n, int d) {
    if (n < 2) return 0;
    if ((long long)d * d > n) return 1;    // no divisor up to sqrt(n)
    if (n % d == 0) return 0;
    return is_prime(n, d + 1);
}
```

`d` is the loop counter, passed along instead of incremented.

</details>

### 13. LCM, the long way

The least common multiple, without the formula $\text{lcm}(a, b) = a \times b \,/ \gcd(a, b)$.

`23 488` → `11224`

<details markdown="1">
<summary>Solution</summary>

```c
// call: lcm(a, b, a); m walks through the multiples of a
long long lcm(long long a, long long b, long long m) {
    if (m % b == 0) return m;
    return lcm(a, b, m + a);
}
```

This can go `b` calls deep. Fine here, but it's a loop in disguise. Compare it with problem 9.

</details>

### 14. Reverse an integer

Return the digits reversed, as an `int`.

`123405` → `504321`

<details markdown="1">
<summary>Solution</summary>

```c
// call: reverse_int(n, 0); acc holds the digits reversed so far
int reverse_int(int n, int acc) {
    if (n == 0) return acc;
    return reverse_int(n / 10, acc * 10 + n % 10);
}
```

`acc` is an *accumulator*: the answer is built on the way down and passed straight back up.

</details>

### 15. Remove odd numbers in place

Remove the odd numbers from an array, with no second array and no printing inside the function. Print the result afterwards.

`1 54 88 6 55 7` → `54 88 6`

<details markdown="1">
<summary>Solution</summary>

```c
// call: n = remove_odds(a, 0, 0, n); returns the new length
int remove_odds(int *a, int i, int j, int n) {
    if (i == n) return j;
    if (a[i] % 2 == 0) a[j++] = a[i];
    return remove_odds(a, i + 1, j, n);
}
```

`i` reads and `j` writes. `j` never passes `i`, so nothing gets overwritten before it is read.

</details>

### 16. Linear search

Return the index of `v` in an array, or `-1` if it isn't there.

In `2 9 4 7 6`: find `5` → `-1`, find `9` → `1`

<details markdown="1">
<summary>Solution</summary>

```c
// call: find(a, 0, n, v)
int find(const int *a, int i, int n, int v) {
    if (i == n) return -1;
    if (a[i] == v) return i;
    return find(a, i + 1, n, v);
}
```

Try next: search from the end.

</details>

## **Shrink from both sides**

### 17. Binary search

Same as problem 16, but the array is sorted.

In `1 2 3 4 5`: find `3` → `2`, find `-5` → `-1`

<details markdown="1">
<summary>Solution</summary>

```c
// call: binary_search(a, 0, n - 1, v)
int binary_search(const int *a, int lo, int hi, int v) {
    if (lo > hi) return -1;
    int mid = lo + (hi - lo) / 2;
    if (a[mid] < v) return binary_search(a, mid + 1, hi, v);
    if (a[mid] > v) return binary_search(a, lo, mid - 1, v);
    return mid;
}
```

Every call halves the range, so the depth is $O(\log n)$. Writing `lo + (hi - lo) / 2` instead of `(lo + hi) / 2` avoids overflow on huge arrays.

</details>

### 18. Palindrome sentence

Is a sentence a palindrome, counting only letters and digits?

`madam, i'm adam` → `palindrome`, `hulala` → `not palindrome`

<details markdown="1">
<summary>Solution</summary>

```c
#include <ctype.h>

// call: is_palindrome(s, 0, (int)strlen(s) - 1)
int is_palindrome(const char *s, int i, int j) {
    if (i >= j) return 1;
    if (!isalnum((unsigned char)s[i])) return is_palindrome(s, i + 1, j);
    if (!isalnum((unsigned char)s[j])) return is_palindrome(s, i, j - 1);
    if (s[i] != s[j]) return 0;
    return is_palindrome(s, i + 1, j - 1);
}
```

Try next: ignore case, so `Madam, I'm Adam` passes too.

</details>

## **More than one call**

### 19. Fibonacci call orders

`fib(n)` calls `fib(n - 1)`, then `fib(n - 2)`, and stops at $n \leq 2$. Print the $n$ of every call in *preorder* (before its calls), *inorder* (between them) and *postorder* (after them).

![The tree of calls made by fib(5)](/posts/20261114/fib-tree-light.svg){: .light w="600" h="300" }
![The tree of calls made by fib(5)](/posts/20261114/fib-tree-dark.svg){: .dark w="600" h="300" }
_Calls made by `fib(5)`._

`5` →

```text
Preorder:  5 4 3 2 1 2 3 2 1
Inorder:   2 3 1 4 2 5 2 3 1
Postorder: 2 1 3 2 4 2 1 3 5
```

<details markdown="1">
<summary>Solution</summary>

```c
void preorder(int n) {
    if (n <= 2) { printf(" %d", n); return; }
    printf(" %d", n);
    preorder(n - 1);
    preorder(n - 2);
}

void inorder(int n) {
    if (n <= 2) { printf(" %d", n); return; }
    inorder(n - 1);
    printf(" %d", n);
    inorder(n - 2);
}

void postorder(int n) {
    if (n <= 2) { printf(" %d", n); return; }
    postorder(n - 1);
    postorder(n - 2);
    printf(" %d", n);
}
```

Only one line moves: before, between, or after the calls. It's the same rule as in problems 1 to 4.

</details>

### 20. Tower of Hanoi

Three pegs `a`, `b` and `c`, and $n$ disks on `a`, largest at the bottom. Move them all to `c`, one disk at a time, never placing a larger disk on a smaller one. Print each move, such as `a -> c`.

`3` →

```text
a -> c
a -> b
c -> b
a -> c
b -> a
b -> c
a -> c
```

<details markdown="1">
<summary>Solution</summary>

Trust `hanoi(n - 1)` to move a stack of $n - 1$ disks between any two pegs. Then $n$ disks take three steps: move the top $n - 1$ out of the way, move the largest disk, and move the $n - 1$ back on top of it.

![Tower of Hanoi as three steps, with the top n-1 disks drawn as one sealed block](/posts/20261114/hanoi-light.svg){: .light w="720" h="186" }
![Tower of Hanoi as three steps, with the top n-1 disks drawn as one sealed block](/posts/20261114/hanoi-dark.svg){: .dark w="720" h="186" }

```c
// call: hanoi(n, 'a', 'b', 'c')
void hanoi(int n, char from, char via, char to) {
    if (n == 0) return;
    hanoi(n - 1, from, to, via);
    printf("%c -> %c\n", from, to);
    hanoi(n - 1, via, from, to);
}
```

That's $2^n - 1$ moves. Tracing them all by hand is a mess; trusting the function takes three lines.

</details>

---

*Originally posted on my old blog, [I, ME AND MYSELF !!!](https://zobayer.blogspot.com/2009/12/cse-102-practice-recursions.html), on December 8, 2009, with the answers in separate documents. Regrouped here by idea, with the solutions inline and modernized.*
