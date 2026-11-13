---
layout: post
title:  Don't Fear Recursion
date:   2026-11-14 00:30:00 +0600
categories: [Algorithms]
tags: [Recursion, Call Stack, Beginners, C]
math: true
---
Recursion scares people for one reason: they try to run the whole thing in their head before writing a single line. All the way down, all the way back up, holding every half-finished call at once. Nobody can do that, and you don't need to.

Two habits are enough: one for writing a recursive function, and one for reading it.

> **Trust the function** when you write it. **Focus on one step** when you trace it.
{: .prompt-tip }

## **Trust the function**

Don't think about recursion before writing the function. Just assume it already does what you want.

Say `f(n)` solves your problem for `n`. To solve `n`, you need the answer for `n - 1`. And who solves `n - 1`? `f(n - 1)` does, because you just assumed so. Call it and use the answer. Need `n - 2` as well? Call `f(n - 2)`.

Then add one rule you already know the answer to, one that doesn't depend on any other problem. That's the *base case*, and it's what stops the calls. Done.

1. **Promise** what `f(n)` returns, in one sentence.
2. **Base case:** answer the input you already know, without any further calls.
3. **Everything else:** call `f` on a smaller input and trust the answer.

Take $n!$. You don't need to know what $7!$ is. You know $0! = 1$, and you know $n! = n \times (n-1)!$. That's the whole function.

![While you write factorial(n), the call inside is a sealed box. Don't open it.](/posts/20261114/trust-light.svg){: .light w="720" h="222" }
![While you write factorial(n), the call inside is a sealed box. Don't open it.](/posts/20261114/trust-dark.svg){: .dark w="720" h="222" }

```c
// promise: factorial(n) returns n!
int factorial(int n) {
    if (n == 0) return 1;           // the rule you already know
    return n * factorial(n - 1);    // trust it to return (n-1)!
}
```

Fibonacci needs two smaller answers, so trust two calls.

![Two smaller answers, two sealed boxes. Trust both.](/posts/20261114/trust-fib-light.svg){: .light w="720" h="222" }
![Two smaller answers, two sealed boxes. Trust both.](/posts/20261114/trust-fib-dark.svg){: .dark w="720" h="222" }

```c
// promise: fib(n) returns the n'th Fibonacci number, fib(1) = fib(2) = 1
int fib(int n) {
    if (n <= 2) return 1;
    return fib(n - 1) + fib(n - 2);
}
```

> The trust only holds if every call gets *closer* to a base case. `factorial(-1)` steps right past `0` and never stops, until the program crashes.
{: .prompt-warning }

"Smaller" doesn't have to mean `n - 1`. It can be the rest of an array (index `i + 1`), half of it (binary search), or the same string with both ends trimmed (palindromes). And when the smaller answer isn't enough to build yours, **promise more**. To find the second-largest number, the second-largest of the rest won't do; return the largest and the second-largest together.

## **Trace one step at a time**

Writing is the easy half. The next problem is visualizing the calls, when you debug, or read someone else's code. The trick is to compartmentalize.

When you're on the step for `n - 1`, think only about `n - 1`: its variables, its lines. Not `n`, not `n - 2`.

But keep a ladder on paper: where did you reach `n - 1` from? When you know the answer for `n - 1`, the ladder tells you who to hand it to. Now you're back at `n`, and once again, you focus on `n` alone. Not `n - 1`, not `n + 1`.

![A staircase of calls from factorial(4) to factorial(0), with only factorial(2) in focus](/posts/20261114/focus-light.svg){: .light w="720" h="462" }
![A staircase of calls from factorial(4) to factorial(0), with only factorial(2) in focus](/posts/20261114/focus-dark.svg){: .dark w="720" h="462" }
_Tracing `factorial(4)`, now at `factorial(2)`. The answer comes up from below; the ladder says where to send it._

Written out, the whole trace is a staircase, down to the base case and back up.

![The full trace of factorial(4): calls go down the left side to the base case, answers come back up the right side](/posts/20261114/ladder-light.svg){: .light w="720" h="470" }
![The full trace of factorial(4): calls go down the left side to the base case, answers come back up the right side](/posts/20261114/ladder-dark.svg){: .dark w="720" h="470" }

Every rung only needs the answer from the rung right below it. You never hold more than one step in your head; the ladder holds the rest.

## **Before the call, after the call**

Any loop can be written as recursion. A loop, and its recursive twin:

```c
for (int i = 0; i < n; i++) {
    printf("%d ", i);
}
```

```c
void forward(int i, int n) {
    if (i == n) return;    // the loop condition, flipped
    printf("%d ", i);      // the loop body
    forward(i + 1, n);     // the next iteration
}
```

Swap the last two lines, and the same calls print backward:

```c
void backward(int i, int n) {
    if (i == n) return;
    backward(i + 1, n);    // all the way down first...
    printf("%d ", i);      // ...then print on the way back up
}
```

`forward(0, 5)` prints `0 1 2 3 4`, and `backward(0, 5)` prints `4 3 2 1 0`. Each step pauses at its call, and the line after the call runs only when the answer comes back, deepest step first.

![Two staircases of calls: printing before the call outputs 0 1 2, printing after it outputs 2 1 0](/posts/20261114/down-up-light.svg){: .light w="720" h="350" }
![Two staircases of calls: printing before the call outputs 0 1 2, printing after it outputs 2 1 0](/posts/20261114/down-up-dark.svg){: .dark w="720" h="350" }
_Same calls, same order. Only the position of the work changes._

Work **before** the call happens on the way down, in calling order. Work **after** the call happens on the way back up, in reverse. That one rule solves a good share of the [practice problems](https://storage.googleapis.com/glitchfest-pub/posts/20261114/recursion-practice-problems.pdf).

## **The ladder is the call stack**

The ladder isn't just a study aid. It's exactly what the machine keeps. Each call gets a *frame*: its own copy of the parameters and locals, plus the spot in the caller to return to. A call pushes a frame, a return pops one, and only the top frame runs. Everything under it is paused mid-line, waiting for an answer, just like the blurred steps of the ladder.

![The call stack with main at the bottom and factorial(0) running at the top](/posts/20261114/stack-light.svg){: .light w="720" h="292" }
![The call stack with main at the bottom and factorial(0) running at the top](/posts/20261114/stack-dark.svg){: .dark w="720" h="292" }
_The stack during `factorial(3)`._

> **Recursion gives you a stack for free.** Some algorithms need a stack, and recursion lets them use the call stack instead of an explicit stack data structure. Depth-first search (DFS) is the classic example: every paused call remembers the node it came from, so when the search hits a dead end, it simply returns and carries on from there.
>
> ```c
> void dfs(int u) {
>     visited[u] = 1;
>     for (int i = 0; i < deg[u]; i++) {
>         int v = adj[u][i];
>         if (!visited[v]) dfs(v);  // this frame remembers u
>     }
> }
> ```
>
> Write the same DFS with a loop, and you have to push and pop that stack yourself.
{: .prompt-info }

## **Recursion can be expensive**

Two costs to watch for:

- **Depth.** Every frame holds stack memory until it returns, and the stack is small: 8 MB by default on Linux and macOS, and 1 MB on Windows with MSVC (2 MB with MinGW). Even a function as small as `factorial` overflows the 8 MB stack a little past 250,000 levels in an unoptimized build, and crashes with a *stack overflow* where the same loop would run fine. An optimizing compiler can sometimes turn simple recursion into a loop, but don't count on it. Depth $O(\log n)$ is always safe, and depth $O(n)$ is fine while $n$ stays small. Python cuts it even shorter, at 1000 levels by default.
- **Repeated work.** `fib(n)` asks for `fib(n - 2)` directly, and again inside `fib(n - 1)`, and the repeats compound all the way down: `fib(40)` makes over 200 million calls.

![The tree of calls made by fib(5)](/posts/20261114/fib-tree-light.svg){: .light w="600" h="300" }
![The tree of calls made by fib(5)](/posts/20261114/fib-tree-dark.svg){: .dark w="600" h="300" }
_Calls made by `fib(5)`. `fib(3)` is computed twice, `fib(2)` three times._

The fix: store each answer the first time you compute it and look it up after that. That's *memoization*, $O(n)$ calls instead of exponential, and the doorway to dynamic programming. For a truly huge $n$, [matrix exponentiation](/posts/matrix-exponentiation/) gets there in $O(\log n)$.

## **Practice, practice, and practice!!!**

Recursion is often how a problem is defined mathematically in the first place, and any other formulation would be much longer. It is also one of the most useful tools for designing divide-and-conquer and dynamic programming solutions, because it lets you see how a problem relates to its subproblems. But it's a habit more than a technique: trust the call when you write it, and focus on one step when you trace it. Build the habit on [20 practice problems (PDF)](https://storage.googleapis.com/glitchfest-pub/posts/20261114/recursion-practice-problems.pdf), ordered from printing an array backwards to the Tower of Hanoi.

**Yes, an iterative solution is usually faster to execute, but recursion was the first solution.**

## **And if you ever forget what recursion is**

> **Recursion** *(noun)*: see [recursion](#top).
{: .prompt-tip }

---

*Originally posted on my old blog, [I, ME AND MYSELF !!!](https://zobayer.blogspot.com/2009/12/cse-102-attacking-recursion.html), on December 10, 2009, as notes for a first-year programming course. Rewritten here for anyone learning recursion, around the two habits I still recommend.*
