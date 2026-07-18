---
layout: post
title:  Matrix Exponentiation for Fast Recurrences
date:   2026-07-19 03:00:00 +0600
categories: [Algorithms]
tags: [competitive-programming, matrix-exponentiation, recurrence, dynamic-programming]
math: true
---
The name sounds like a linear-algebra chore, but this isn't about computing a matrix's power for its own sake. It's a technique that turns matrix powers into a way to jump straight to the n'th term of a recurrence — in logarithmic time, even for enormous `n`.

Sometimes a problem has an easy recurrence (e.g. a DP problem), but constraints make DP hopeless. Take the n'th Fibonacci number, `f(n) = f(n-1) + f(n-2)`. For small `n`, plain recursion or DP handles it fine. But what if the problem asks: *given 0 < n < 1000000000, find f(n) % 999983*? No amount of dynamic programming will save you here!

That's where matrix exponentiation comes in. We'll get to why it works later — first, let's see how it represents a recurrence relation.

> This technique works only for **linear** recurrences — each term must be a linear combination of earlier terms (optionally plus a constant, as we'll see in Example 4). Matrix exponentiation cannot be used to directly compute non-linear recurrences (e.g. $f(n) = f(n-1)^2 + 3$). The requirement is that the transition between steps must be a strictly linear combination of the previous terms.
{: .prompt-warning }

## **Prerequisites**

Before continuing, you need to know:

- Given two matrices, how to find their product — or, given the product of two matrices and one of them, how to find the other.
- Given a matrix `M` of size `d x d`, how to find $(M^n \bmod m)$ in $O(d^3 \log n)$ — the modulo `m` is usually there to keep the values from overflowing.

## **Patterns**

What we need first is a recursive relation, and what we want is a matrix $M$ that can lead us from a set of already-known states to the desired next state. Suppose we know `k` states of a given recurrence relation and want to find the `(k+1)`'th state. Let $M$ be a `k x k` matrix, and build a `k x 1` matrix $A$ from the known states of the recurrence relation. Now we want a `k x 1` matrix $B$ that represents the set of next states, i.e. $M \times A = B$, as shown below:

$$
M \times
\underbrace{\begin{bmatrix} f(n) \\ f(n-1) \\ f(n-2) \\ \vdots \\ f(n-k+1) \end{bmatrix}}_{A}
=
\underbrace{\begin{bmatrix} f(n+1) \\ f(n) \\ f(n-1) \\ \vdots \\ f(n-k+2) \end{bmatrix}}_{B}
$$

So, if we can design $M$ accordingly, the job's done! The matrix will then represent the recurrence relation.

### Example 1 — Plain Fibonacci

Let's start with the simplest one, `f(n) = f(n-1) + f(n-2)`, so `f(n+1) = f(n) + f(n-1)`. Suppose we know `f(n)` and `f(n-1)`, and we want `f(n+1)`. From the equations above, matrices $A$ and $B$ can be formed as shown below:

$$
A = \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
\qquad
B = \begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
$$

> Matrix $A$ is always designed so that every state on which `f(n+1)` depends is present.
{: .prompt-tip }

So now we need to design a `2 x 2` matrix $M$ such that it satisfies $M \times A = B$. The first element of $B$ is `f(n+1)`, which is actually `f(n) + f(n-1)`. To get it from matrix $A$, we need one `f(n)` and one `f(n-1)`. So the first row of $M$ is `[1 1]`:

$$
\begin{bmatrix} 1 & 1 \\ \text{---} & \text{---} \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ \text{---} \end{bmatrix}
$$

> `---` means we don't care about this value yet.
{: .prompt-info }

Similarly, the second item of $B$ is `f(n)`, which we get by simply taking one `f(n)` from $A$. So the second row of $M$ is `[1 0]`:

$$
\begin{bmatrix} \text{---} & \text{---} \\ 1 & 0 \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} \text{---} \\ f(n) \end{bmatrix}
$$

Thus we get the desired `2 x 2` matrix $M$:

$$
\begin{bmatrix} 1 & 1 \\ 1 & 0 \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
$$

If you are confused about how the matrix above is derived, you might try it this way. We know the multiplication of an `n x n` matrix $M$ with an `n x 1` matrix $A$ produces an `n x 1` matrix $B$, i.e. $M \times A = B$. The i'th element of the product $B$ is the product of the i'th row of $M$ with $A$. Here, the first element of $B$ is `f(n+1) = f(n) + f(n-1)`, so it is the product of the first row of $M$ and $A$. Let the first row of $M$ be `[x y]`. Then, by matrix multiplication:

$$
x \cdot f(n) + y \cdot f(n-1) = f(n+1) = f(n) + f(n-1) \implies x = 1,\ y = 1
$$

Thus the first row of $M$ is `[1 1]`. Similarly, let the second row of $M$ be `[x y]`:

$$
x \cdot f(n) + y \cdot f(n-1) = f(n) \implies x = 1,\ y = 0
$$

Thus the second row of $M$ is `[1 0]`.

### Example 2 — Constant coefficients

Now let's make it a bit more complex: find `f(n) = a * f(n-1) + b * f(n-2)`, where `a` and `b` are constants. This tells us `f(n+1) = a * f(n) + b * f(n-1)`. By now it should be clear that the dimension of the matrices equals the number of dependencies — again 2 in this example. So $A$ and $B$ are both `2 x 1`:

$$
A = \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
\qquad
B = \begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
$$

For `f(n+1) = a * f(n) + b * f(n-1)`, we need `[a b]` in the first row of the objective matrix $M$ instead of `[1 1]` from the previous example, because now we need `a` of the `f(n)`'s and `b` of the `f(n-1)`'s:

$$
\begin{bmatrix} a & b \\ \text{---} & \text{---} \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ \text{---} \end{bmatrix}
$$

And for the second item of $B$, i.e. `f(n)`, we already have it in $A$, so we just take it. The second row of $M$ is `[1 0]`, same as before:

$$
\begin{bmatrix} a & b \\ 1 & 0 \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
$$

Pretty simple, just like the previous one.

### Example 3 — Gaps in the recurrence

Now let's face a slightly more complex relation: find `f(n) = a * f(n-1) + c * f(n-3)`. Oops! A few moments ago all we saw were contiguous states, but here the state `f(n-2)` is missing. Now what?

Actually, this is not a problem at all. We can rewrite the relation as `f(n) = a * f(n-1) + 0 * f(n-2) + c * f(n-3)`, which gives `f(n+1) = a * f(n) + 0 * f(n-1) + c * f(n-2)`. Now this is exactly the form described in Example 2. So the objective matrix $M$ is `3 x 3`:

$$
\begin{bmatrix} a & 0 & c \\ 1 & 0 & 0 \\ 0 & 1 & 0 \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \\ f(n-2) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ f(n) \\ f(n-1) \end{bmatrix}
$$

These entries are computed the same way as in Example 2. If you find it difficult, try it on pen and paper!

### Example 4 — An added constant

The plot thickens! This time the problem sneaks in a constant term: find `f(n) = f(n-1) + f(n-2) + c`, where `c` is a constant.

This one is new. In everything we've seen so far, after multiplication each state in $A$ transforms into its next state in $B$:

```text
f(n)   = f(n-1) + f(n-2) + c
f(n+1) = f(n)   + f(n-1) + c
f(n+2) = f(n+1) + f(n)   + c
.................................  and so on
```

So we can't get it through the previous fashion directly. But how about we add `c` as a state?

$$
M \times
\begin{bmatrix} f(n) \\ f(n-1) \\ c \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ f(n) \\ c \end{bmatrix}
$$

Now it's not hard to design $M$ the previous way. Here it is, but don't forget to verify it yourself:

$$
\begin{bmatrix} 1 & 1 & 1 \\ 1 & 0 & 0 \\ 0 & 0 & 1 \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \\ c \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ f(n) \\ c \end{bmatrix}
$$

### Example 5 — Everything at once

Let's put it all together: find a matrix suitable for `f(n) = a * f(n-1) + c * f(n-3) + d * f(n-4) + e`. I'll leave this one as an exercise. Here's the final matrix $M$ — check it against yours, and see if you can work out matrices $A$ and $B$ as well:

$$
M =
\begin{bmatrix}
a & 0 & c & d & 1 \\
1 & 0 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 & 0 \\
0 & 0 & 0 & 0 & 1
\end{bmatrix}
$$

> Take a look back at Example 3 and Example 4 if you get stuck.
{: .prompt-tip }

### Example 6 — Conditional (odd/even) recurrences

Sometimes a recurrence is given like this:

```text
f(n) = f(n-1)  if n is odd
f(n) = f(n-2)  if n is even

In short:
f(n) = (n & 1) * f(n-1) + (!(n & 1)) * f(n-2)
```

Here we can just split on the basis of parity and keep two different matrices — one for each case. As always, the state is $A = \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}$, and we advance it to $\begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}$. Which matrix we use depends on the parity of the index we are producing, `n+1`.

When `n+1` is odd, `f(n+1) = f(n)`, so we just copy `f(n)` into the top slot:

$$
M_{\text{odd}} =
\begin{bmatrix} 1 & 0 \\ 1 & 0 \end{bmatrix}
$$

When `n+1` is even, `f(n+1) = f(n-1)`, so we pull from the second slot instead:

$$
M_{\text{even}} =
\begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}
$$

So we simply alternate between $M_{\text{odd}}$ and $M_{\text{even}}$ as we step through the sequence.

### Example 7 — Coupled recurrences

Sometimes we need to maintain more than one recurrence where they are interrelated. For example, let a recurrence relation be `g(n) = 2*g(n-1) + 2*g(n-2) + f(n)`, where `f(n) = 2*f(n-1) + 2*f(n-2)`. Here `g(n)` depends on `f(n)`, and both can be maintained in the same matrix — just with increased dimensions. Let's design $A$ and $B$, then find $M$:

$$
A = \begin{bmatrix} g(n) \\ g(n-1) \\ f(n+1) \\ f(n) \end{bmatrix}
\qquad
B = \begin{bmatrix} g(n+1) \\ g(n) \\ f(n+2) \\ f(n+1) \end{bmatrix}
$$

Here `g(n+1) = 2*g(n) + 2*g(n-1) + f(n+1)` and `f(n+2) = 2*f(n+1) + 2*f(n)`. Using the same process as before, we get the objective matrix $M$:

$$
M =
\begin{bmatrix}
2 & 2 & 1 & 0 \\
1 & 0 & 0 & 0 \\
0 & 0 & 2 & 2 \\
0 & 0 & 1 & 0
\end{bmatrix}
$$

So these are the basic shapes of recurrence relations that can be solved with this simple technique.

## **Analysis**

Now that we've seen how matrix multiplication can maintain a recurrence relation, let's return to our first question: how does this help us solve recurrences over a huge range?

Recall the recurrence `f(n) = f(n-1) + f(n-2)`. We already know that:

$$
M \times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
\qquad \text{...(1)}
$$

How about we apply $M$ one more time, substituting equation (1) into the inner product?

$$
\begin{aligned}
M \times M \times \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
&= M \times \left( M \times \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix} \right) \\[6pt]
&= M \times \begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix} \\[6pt]
&= \begin{bmatrix} f(n+2) \\ f(n+1) \end{bmatrix}
\end{aligned}
$$

So we finally get:

$$
M^2 \times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+2) \\ f(n+1) \end{bmatrix}
$$

Similarly, we can show:

$$
\begin{aligned}
M^3 \times \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix} &= \begin{bmatrix} f(n+3) \\ f(n+2) \end{bmatrix} \\[6pt]
M^4 \times \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix} &= \begin{bmatrix} f(n+4) \\ f(n+3) \end{bmatrix}
\end{aligned}
$$

And in general:

$$
M^k \times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+k) \\ f(n+k-1) \end{bmatrix}
$$

Thus we can get any state `f(n)` by simply raising the objective matrix $M$ to the power `n-1` in $O(d^3 \log n)$, where `d` is the dimension of the square matrix $M$. So even if `n = 1000000000`, this can be calculated pretty easily, as long as $d^3$ is sufficiently small.

## **Related problems**

- UVa 10229 — Modular Fibonacci
- UVa 10870 — Recurrences
- UVa 11651 — Krypton Number System
- UVa 10754 — Fantastic Sequence
- UVa 11551 — Experienced Endeavour

## **An example: Krypton Number System**

Let's put all this to work on a real problem — [UVa 11651 — Krypton Number System](https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem=2698). It asks us to count the integers written in base `b` (with $2 \le b \le 6$) such that

- no two adjacent digits are equal,
- there is no leading zero, and
- the **score** — the sum of squared differences of adjacent digits — is exactly `s` (with $1 \le s \le 10^9$).

The count is reported modulo $2^{32}$. For example, the number `1241` has a score of $(1-2)^2 + (2-4)^2 + (4-1)^2 = 1 + 4 + 9 = 14$.

**The recurrence.** Let $g(t, j)$ be the number of valid numbers that end in digit `j` and have score exactly `t`. Appending a digit `j` after a digit `i` (with $i \neq j$) adds $(i-j)^2$ to the score, so:

$$
g(t, j) = \sum_{\substack{i = 0 \\ i \neq j}}^{b-1} g\!\left(t - (i-j)^2,\ i\right)
$$

with $g(t, \cdot) = 0$ for $t < 0$, and the base case $g(0, j) = 1$ for every non-zero digit `j` (a lone digit is a valid number of score 0, but it can't be `0`, thanks to the leading-zero rule). The answer we want is:

$$
\text{count} = \sum_{j=0}^{b-1} g(s, j) \pmod{2^{32}}
$$

This is linear, so matrix exponentiation applies — but with a twist. The score `s` is far too large to index states directly. The saving grace: appending one digit bumps the score by at most $(b-1)^2$, so $g(t, \cdot)$ depends only on the previous $C = (b-1)^2$ score levels. Pack those levels into one state vector, with `b` digit-counts at each level:

$$
V(t) = \begin{bmatrix} G(t) \\ G(t-1) \\ \vdots \\ G(t-C+1) \end{bmatrix},
\qquad
G(t) = \begin{bmatrix} g(t, 0) \\ g(t, 1) \\ \vdots \\ g(t, b-1) \end{bmatrix}
$$

**The matrix.** A single block-companion matrix $M$ of size $Cb \times Cb$ advances the whole window by one score level, $V(t) = M \times V(t-1)$:

$$
M =
\begin{bmatrix}
A_1 & A_2 & \cdots & A_{C-1} & A_C \\
I & 0 & \cdots & 0 & 0 \\
0 & I & \cdots & 0 & 0 \\
\vdots & & \ddots & & \vdots \\
0 & 0 & \cdots & I & 0
\end{bmatrix}
$$

The top row does the real work; the identity blocks below it just shift the window down one level. Each $A_w$ is a $b \times b$ block that collects the digit pairs whose squared difference is exactly `w`:

$$
(A_w)_{j,i} =
\begin{cases}
1 & \text{if } i \neq j \text{ and } (i-j)^2 = w \\
0 & \text{otherwise}
\end{cases}
$$

Now raise $M$ to the `s`'th power (fast exponentiation, every operation taken modulo $2^{32}$), apply it to the starting vector $V(0)$ — whose only non-zero block is $G(0) = \begin{bmatrix} 0 & 1 & 1 & \cdots & 1 \end{bmatrix}^{T}$ — and sum the entries of the top block $G(s)$. For `b = 6`, $M$ is only $150 \times 150$, so even `s` up to $10^9$ is just a handful of $O(\log s)$ multiplications.

> Sample check: for base 6, score 1, the only way to total exactly 1 is a two-digit number whose digits differ by 1. Listing them — `10, 12, 21, 23, 32, 34, 43, 45, 54` — gives **9**, which matches the problem's sample output.
{: .prompt-tip }

---

*Originally posted on my old blog, [I, ME AND MYSELF !!!](https://zobayer.blogspot.com/2010/11/matrix-exponentiation.html), on November 20, 2010. Reposted here with the matrices typeset properly and a few typos cleaned up.*
