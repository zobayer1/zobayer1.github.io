---
layout: post
title:  Matrix Exponentiation for Fast Recurrences
date:   2026-07-19 03:00:00 +0600
categories: [Algorithms]
tags: [Competitive Programming, Matrix Exponentiation, Recurrence, Dynamic Programming]
math: true
---
The title sounds like a linear-algebra exercise, but this isn't about computing a matrix's power for its own sake. It's a technique that turns matrix powers into a way to jump straight to the $n$'th term of a recurrence in logarithmic time. Very handy when $n$ is enormous.

Sometimes a problem has an easy recurrence (e.g. a dynamic programming problem), but constraints make DP hopeless. Take the $n$'th Fibonacci number, $f(n) = f(n-1) + f(n-2)$. For small $n$, plain recursion or DP handles it fine. But what if the problem asks: *given $0 < n < 10^9$, find $f(n) \bmod 999983$*; DP will not save you here!

That's where matrix exponentiation comes in. We'll get to how and why it works later, but first, let's see how it represents a recurrence relation.

> This technique works only for **linear** recurrences. Matrix exponentiation cannot be used to directly compute non-linear recurrences (e.g. $f(n) = f(n-1)^2 + 3$). The requirement is that the transition between steps must be a strictly linear combination of the previous terms.
{: .prompt-warning }

> The reader is encouraged to try and verify the equations shown in this post with pen and paper.
{: .prompt-tip }

## **Good to Know**

- Basic matrix operations: Given two matrices, find their product. Remember, matrix multiplication is not commutative: generally $A \times B \neq B \times A$. It commutes when one of them is an [identity matrix](https://en.wikipedia.org/wiki/Identity_matrix), when they are [inverses](https://en.wikipedia.org/wiki/Invertible_matrix) of each other, or when both are [diagonal matrices](https://en.wikipedia.org/wiki/Diagonal_matrix).
- Fast modular exponentiation: Given a matrix $M$ of size $d \times d$, find $(M^n \bmod m)$ in $O(d^3 \log n)$ time. Modulo $m$ prevents overflow. Example [implementation](https://www.geeksforgeeks.org/dsa/modular-exponentiation-power-in-modular-arithmetic/).

## **Design State Matrices**

We start with a recurrence relation, and our goal is to find a matrix $M$ that carries a set of already-known states forward to the next state. Suppose we know $k$ states of a given recurrence relation and want to find the $(k+1)$'th state. Let $M$ be a $k \times k$ matrix, and build a $k \times 1$ matrix $A$ from the known states of the recurrence relation. Now we want a $k \times 1$ matrix $B$ that represents the set of next states, i.e. $M \times A = B$, as shown below:

$$
M \times
\underbrace{\begin{bmatrix} f(n) \\ f(n-1) \\ f(n-2) \\ \vdots \\ f(n-k+1) \end{bmatrix}}_{A}
=
\underbrace{\begin{bmatrix} f(n+1) \\ f(n) \\ f(n-1) \\ \vdots \\ f(n-k+2) \end{bmatrix}}_{B}
$$

So, if we can design $M$ accordingly, the job's done! The matrix will then represent the recurrence relation.

### Example 1 — Plain Fibonacci

Let's start with the simplest one, $f(n) = f(n-1) + f(n-2)$, so $f(n+1) = f(n) + f(n-1)$. Suppose we know $f(n)$ and $f(n-1)$, and we want $f(n+1)$. From the equations above, matrices $A$ and $B$ can be formed as shown below:

$$
A = \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
\qquad
B = \begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
$$

> Matrix $A$ is always designed so that every state on which $f(n+1)$ depends is present.
{: .prompt-tip }

So now we need to design a $2 \times 2$ matrix $M$ such that it satisfies $M \times A = B$. The first element of $B$ is $f(n+1)$, which is actually $f(n) + f(n-1)$. To get it from matrix $A$, we need one $f(n)$ and one $f(n-1)$. So the first row of $M$ is $\begin{bmatrix} 1 & 1 \end{bmatrix}$:

$$
\begin{bmatrix} 1 & 1 \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \end{bmatrix}
$$

Similarly, the second item of $B$ is $f(n)$, which we get by simply taking one $f(n)$ from $A$. So the second row of $M$ is $\begin{bmatrix} 1 & 0 \end{bmatrix}$:

$$
\begin{bmatrix} 1 & 0 \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n) \end{bmatrix}
$$

Thus we get the desired $2 \times 2$ matrix $M$:

$$
\begin{bmatrix} 1 & 1 \\ 1 & 0 \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
$$

If you are confused about how the matrix above is derived, you might try it this way. We know the multiplication of an $n \times n$ matrix $M$ with an $n \times 1$ matrix $A$ produces an $n \times 1$ matrix $B$, i.e. $M \times A = B$. The $i$'th element of the product $B$ is the product of the $i$'th row of $M$ with $A$. Here, the first element of $B$ is $f(n+1) = f(n) + f(n-1)$, so it is the product of the first row of $M$ and $A$. Let the first row of $M$ be $\begin{bmatrix} x & y \end{bmatrix}$. Then, by matrix multiplication, we need $\begin{bmatrix} x & y \end{bmatrix}$ such that:

$$
x \cdot f(n) + y \cdot f(n-1) = f(n+1)
$$

By setting $x = 1$ and $y = 1$, we can see the equation $f(n+1) = f(n) + f(n-1)$ is satisfied. So the first row of $M$ is $\begin{bmatrix} 1 & 1 \end{bmatrix}$. Similarly, let the second row of $M$ be $\begin{bmatrix} x & y \end{bmatrix}$, which must satisfy:

$$
x \cdot f(n) + y \cdot f(n-1) = f(n)
$$

Here, setting $x = 1$ and $y = 0$ works. So the second row of $M$ is $\begin{bmatrix} 1 & 0 \end{bmatrix}$.

### Example 2 — Constant coefficients

Now let's make it a bit more complex: find $f(n) = a \cdot f(n-1) + b \cdot f(n-2)$, where $a$ and $b$ are constants. This tells us $f(n+1) = a \cdot f(n) + b \cdot f(n-1)$. By now it should be clear that the dimension of the matrices equals the number of dependencies, again 2 in this example. So $A$ and $B$ are both $2 \times 1$:

$$
A = \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
\qquad
B = \begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
$$

For $f(n+1) = a \cdot f(n) + b \cdot f(n-1)$, we need $\begin{bmatrix} a & b \end{bmatrix}$ in the first row of the objective matrix $M$ instead of $\begin{bmatrix} 1 & 1 \end{bmatrix}$ from the previous example, because now we need $a$ of the $f(n)$'s and $b$ of the $f(n-1)$'s:

$$
\begin{bmatrix} a & b \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \end{bmatrix}
$$

And for the second item of $B$, i.e. $f(n)$, we already have it in $A$. As shown in **Example 1**: the second row of $M$ remains $\begin{bmatrix} 1 & 0 \end{bmatrix}$. Therefore, the equation becomes:

$$
\begin{bmatrix} a & b \\ 1 & 0 \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
$$

Pretty simple, just like the previous one.

### Example 3 — Missing terms

Now let's face a slightly more complex relation: find $f(n) = a \cdot f(n-1) + c \cdot f(n-3)$. Oops! A few moments ago all we saw were contiguous states, but here the state $f(n-2)$ is missing. Now what?

This is not a problem at all. We can rewrite the relation as $f(n) = a \cdot f(n-1) + 0 \cdot f(n-2) + c \cdot f(n-3)$, which gives $f(n+1) = a \cdot f(n) + 0 \cdot f(n-1) + c \cdot f(n-2)$. Now this is exactly the form described in **Example 2**. So the objective matrix $M$ is $3 \times 3$:

$$
\begin{bmatrix} a & 0 & c \\ 1 & 0 & 0 \\ 0 & 1 & 0 \end{bmatrix}
\times
\begin{bmatrix} f(n) \\ f(n-1) \\ f(n-2) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ f(n) \\ f(n-1) \end{bmatrix}
$$

These entries are computed the same way as in Example 2. Try it yourself with pen and paper!

### Example 4 — Additional constants

The plot thickens! This time the problem sneaks in a constant term: find $f(n) = f(n-1) + f(n-2) + c$, where $c$ is a constant. For example:

$$
\begin{aligned}
f(n)   &= f(n-1) &&{}+{} f(n-2) &&{}+{} c \\
f(n+1) &= f(n)   &&{}+{} f(n-1) &&{}+{} c \\
f(n+2) &= f(n+1) &&{}+{} f(n)   &&{}+{} c
\end{aligned}
$$

So far we have seen that each value in state matrix $A$ changes to a new value in state matrix $B$. But $c$ is a constant that must not change. Nothing to worry, how about we add $c$ as a state in both $A$ and $B$?

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

### Example 5 — Everything put together

Let's put it all together. Find a matrix suitable for the following recurrence:

$$
f(n) = a \cdot f(n-1) + c \cdot f(n-3) + d \cdot f(n-4) + e
$$

I'll leave this one as an exercise. Work out matrices $M$, $A$, and $B$ yourself, then expand the section below to check against your answer.

> Take a look back at Example 3 and Example 4 if you get stuck.
{: .prompt-tip }

<details markdown="1">
<summary>Reveal matrices M, A and B</summary>

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

$$
A = \begin{bmatrix} f(n) \\ f(n-1) \\ f(n-2) \\ f(n-3) \\ e \end{bmatrix}
\qquad
B = \begin{bmatrix} f(n+1) \\ f(n) \\ f(n-1) \\ f(n-2) \\ e \end{bmatrix}
$$

</details>

### Example 6 — Conditional recurrences

Sometimes a recurrence is given like this:

$$
f(n) =
\begin{cases}
f(n-1) & \text{if } n \text{ is odd} \\
f(n-2) & \text{if } n \text{ is even}
\end{cases}
$$

Or, written as a single line:

$$
f(n) = (n \bmod 2) \cdot f(n-1) + (1 - n \bmod 2) \cdot f(n-2)
$$

Here we can just split on the basis of parity and keep two different matrices; one for each case.

Initial state:

$$
A = \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
$$

and we advance it to

$$
B = \begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
$$

Which matrix we use depends on the parity of the index we are producing, $n+1$.

When $n+1$ is odd, $f(n+1) = f(n)$, so we just copy $f(n)$ into the top slot:

$$
M_{\text{odd}} =
\begin{bmatrix} 1 & 0 \\ 1 & 0 \end{bmatrix}
$$

When $n+1$ is even, $f(n+1) = f(n-1)$, so we pull from the second slot instead:

$$
M_{\text{even}} =
\begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}
$$

So we simply alternate between $M_{\text{odd}}$ and $M_{\text{even}}$ as we step through the sequence.

### Example 7 — Coupled recurrences

Sometimes we need to maintain more than one recurrence where they are interrelated. For example, let a recurrence relation be $g(n) = 2 \cdot g(n-1) + 2 \cdot g(n-2) + f(n)$, where $f(n) = 2 \cdot f(n-1) + 2 \cdot f(n-2)$. Here $g(n)$ depends on $f(n)$, and both can be maintained in the same matrix with increased dimensions. Let's design $A$ and $B$, then find $M$:

$$
A = \begin{bmatrix} g(n) \\ g(n-1) \\ f(n+1) \\ f(n) \end{bmatrix}
\qquad
B = \begin{bmatrix} g(n+1) \\ g(n) \\ f(n+2) \\ f(n+1) \end{bmatrix}
$$

Here $g(n+1) = 2 \cdot g(n) + 2 \cdot g(n-1) + f(n+1)$ and $f(n+2) = 2 \cdot f(n+1) + 2 \cdot f(n)$. Using the same process as before, we get the objective matrix $M$:

$$
M =
\begin{bmatrix}
2 & 2 & 1 & 0 \\
1 & 0 & 0 & 0 \\
0 & 0 & 2 & 2 \\
0 & 0 & 1 & 0
\end{bmatrix}
$$

### Example 8 — Vector states (block matrices)

Everything so far kept a single number per state. But sometimes a "state" is itself a bundle of numbers that evolve together. Suppose we advance a whole vector $G(t) = [x(t), y(t)]$ at each step, where the two sequences are coupled and each also reaches two steps back:

$$
\begin{aligned}
x(t) &= x(t-1) + 2\,y(t-1) + 3\,x(t-2) \\
y(t) &= x(t-1) + \phantom{2\,}y(t-1) + 2\,y(t-2)
\end{aligned}
$$

We can write both lines at once as a single vector recurrence, $G(t) = P \cdot G(t-1) + Q \cdot G(t-2)$, where $P$ holds the coefficients on the previous vector and $Q$ those on the one before it:

$$
P = \begin{bmatrix} 1 & 2 \\ 1 & 1 \end{bmatrix}
\qquad
Q = \begin{bmatrix} 3 & 0 \\ 0 & 2 \end{bmatrix}
$$

Read them row by row: the first rows of $P$ and $Q$ together give $x(t)$, the second rows give $y(t)$.

The trick is exactly the same as Example 1, we just stack *vector* states instead of scalar ones. So each entry of $A$ and $B$ is now a whole block:

$$
A = \begin{bmatrix} G(n) \\ G(n-1) \end{bmatrix}
\qquad
B = \begin{bmatrix} G(n+1) \\ G(n) \end{bmatrix}
$$

The objective matrix is built the same way as before, but with blocks in place of numbers: every coefficient becomes its coefficient block, every plain $1$ becomes an identity block $I$, and every $0$ becomes a zero block $\mathbf{0}$:

$$
M =
\begin{bmatrix} P & Q \\ I & \mathbf{0} \end{bmatrix}
=
\begin{bmatrix}
1 & 2 & 3 & 0 \\
1 & 1 & 0 & 2 \\
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0
\end{bmatrix}
$$

Here $I$ is the $2 \times 2$ identity matrix and $\mathbf{0}$ is the $2 \times 2$ zero matrix. Notice the second block-row, $\begin{bmatrix} I & \mathbf{0} \end{bmatrix}$: it does not compute anything new, it just copies the entire $G(n)$ block down into the next state, exactly like the $\begin{bmatrix} 1 & 0 \end{bmatrix}$ row in Example 1, only promoted from a single number to a whole block. This block-companion shape is what you reach for whenever one step has to advance a group of interdependent values at once.

These are the basic shapes of recurrence relations that can be solved with this simple technique.

## **The Exponentiation**

Now that we've seen how matrix multiplication can maintain a recurrence relation, let's return to our first question: how does this help us solve recurrences over a huge range?

Recall the recurrence $f(n) = f(n-1) + f(n-2)$. We already know that:

$$
M \times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix}
$$

Multiplying with $M$:

$$
\begin{aligned}
M \times \left( M \times \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix} \right)
&= M \times \begin{bmatrix} f(n+1) \\ f(n) \end{bmatrix} \\[6pt]
M^2 \times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
&=
\begin{bmatrix} f(n+2) \\ f(n+1) \end{bmatrix}
\end{aligned}
$$

Similarly:

$$
\begin{aligned}
M^3 \times \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix} &= \begin{bmatrix} f(n+3) \\ f(n+2) \end{bmatrix} \\[6pt]
M^4 \times \begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix} &= \begin{bmatrix} f(n+4) \\ f(n+3) \end{bmatrix}
\end{aligned}
$$

Generalized:

$$
M^k \times
\begin{bmatrix} f(n) \\ f(n-1) \end{bmatrix}
=
\begin{bmatrix} f(n+k) \\ f(n+k-1) \end{bmatrix}
$$

Thus we can get any state $f(n)$ by simply raising the objective matrix $M$ to the power $n-1$ in $O(d^3 \log n)$, where $d$ is the dimension of the square matrix $M$. So even if $n = 10^9$, this can be calculated pretty easily, as long as $d^3$ is sufficiently small.

## **An Example: Krypton Number System**

Let's put all this to work on a real problem — [Krypton Number System](https://onlinejudge.org/external/116/11651.pdf). It asks us to count the integers written in base $b$ (with $2 \le b \le 6$) such that

- no two adjacent digits are equal,
- there is no leading zero, and
- **score**: the sum of squared differences of adjacent digits is exactly $s$ ($1 \le s \le 10^9$).

The count is reported modulo $2^{32}$. For example, the number $1241$ has a score of $(1-2)^2 + (2-4)^2 + (4-1)^2 = 1 + 4 + 9 = 14$.

> Sample check: for base 6, score 1, the only way to total exactly 1 is a two-digit number whose digits differ by 1. Listing them — $10, 12, 21, 23, 32, 34, 43, 45, 54$ — gives **9**.
{: .prompt-tip }

This problem can be solved following the patterns we have seen in Example 7 and 8 above. Expand the following sections for the hints.

<details markdown="1">
<summary>Expand to see the recurrence</summary>
### The recurrence
Let $g(t, j)$ be the number of valid numbers that end in digit $j$ and have score exactly $t$. Appending a digit $j$ after a digit $i$ (with $i \neq j$) adds $(i-j)^2$ to the score, so:

$$
g(t, j) = \sum_{\substack{i = 0 \\ i \neq j}}^{b-1} g\!\left(t - (i-j)^2,\ i\right)
$$

with $g(t, \cdot) = 0$ for $t < 0$, and the base case $g(0, j) = 1$ for every non-zero digit $j$ (a lone digit is a valid number of score 0, but it can't be $0$, thanks to the leading-zero rule). The answer we want is:

$$
\text{count} = \sum_{j=0}^{b-1} g(s, j) \pmod{2^{32}}
$$

This is linear, so matrix exponentiation applies, but with a twist. The score $s$ is far too large to index states directly. The saving grace: appending one digit bumps the score by at most $(b-1)^2$, so $g(t, \cdot)$ depends only on the previous $C = (b-1)^2$ score levels. Pack those levels into one state vector, with $b$ digit-counts at each level:

$$
V(t) = \begin{bmatrix} G(t) \\ G(t-1) \\ \vdots \\ G(t-C+1) \end{bmatrix},
\qquad
G(t) = \begin{bmatrix} g(t, 0) \\ g(t, 1) \\ \vdots \\ g(t, b-1) \end{bmatrix}
$$

This is the block-state pattern from Example 8, and the reason there are two matrices is that the recurrence lives at two nested scales. $G(t)$ is the inner block for the $b$ digit-counts at a *single* score level $t$, since $g(t, j)$ at one level mixes all $b$ possible ending digits. $V(t)$ is the outer state that stacks the last $C$ of those blocks, because appending a digit can push the score back by as much as $C$ levels, so a single step must be able to reach all of them. In short: $G$ captures "which digit," and $V$ captures "how far back the score can jump."
</details>

<details markdown="1">
<summary>Expand to see the matrix</summary>
### The matrix
A single block-companion matrix $M$ of size $Cb \times Cb$ advances the whole window by one score level, $V(t) = M \times V(t-1)$:

$$
M =
\begin{bmatrix}
A_1 & A_2 & \cdots & A_{C-1} & A_C \\
I & \mathbf{0} & \cdots & \mathbf{0} & \mathbf{0} \\
\mathbf{0} & I & \cdots & \mathbf{0} & \mathbf{0} \\
\vdots & & \ddots & & \vdots \\
\mathbf{0} & \mathbf{0} & \cdots & I & \mathbf{0}
\end{bmatrix}
$$

The top row does the real work; the identity blocks below it just shift the window down one level. Each $A_w$ is a $b \times b$ block that collects the digit pairs whose squared difference is exactly $w$:

$$
(A_w)_{j,i} =
\begin{cases}
1 & \text{if } i \neq j \text{ and } (i-j)^2 = w \\
0 & \text{otherwise}
\end{cases}
$$

Now raise $M$ to the $s$'th power (fast exponentiation, every operation taken modulo $2^{32}$), apply it to the starting vector $V(0)$ whose only non-zero block is $G(0) = \begin{bmatrix} 0 & 1 & 1 & \cdots & 1 \end{bmatrix}^{\top}$ and sum the entries of the top block $G(s)$. For $b = 6$, $M$ is only $150 \times 150$, so even $s$ up to $10^9$ is just a handful of $O(\log s)$ multiplications.
</details>

## **Practice Problems**

- [UVa 10229 — Modular Fibonacci](https://onlinejudge.org/external/102/10229.pdf)
- [UVa 10870 — Recurrences](https://onlinejudge.org/external/108/10870.pdf)
- [UVa 11651 — Krypton Number System](https://onlinejudge.org/external/116/11651.pdf)
- [UVa 10754 — Fantastic Sequence](https://onlinejudge.org/external/107/10754.pdf)
- [UVa 11551 — Experienced Endeavour](https://onlinejudge.org/external/115/11551.pdf)

---

*Originally posted on my old blog, [I, ME AND MYSELF !!!](https://zobayer.blogspot.com/2010/11/matrix-exponentiation.html), on November 20, 2010. Reposted here with the matrices typeset properly and a few typos cleaned up.*
