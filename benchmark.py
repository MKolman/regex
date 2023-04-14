import time
from regex import Regex
import re


def bench_test(regex: str, text: str, N: int, T: float) -> tuple[float, int]:
    re = Regex(regex)
    start = time.process_time()
    for n in range(N):
        re.full_match(text)
        if time.process_time() - start > T:
            N = n
            break
    end = time.process_time()
    return (end - start) / N, N


def bench_test_re(regex: str, text: str, N: int, T: float) -> tuple[float, int]:
    reg = re.compile(regex)
    start = time.process_time()
    for n in range(N):
        reg.match(text)
        if time.process_time() - start > T:
            N = n
            break
    end = time.process_time()
    return (end - start) / N, N


def fmt_bench(t: float, N: int):
    if t > 1:
        return f"{N}@{t:.2f}s"
    elif t > 1e-3:
        return f"{N}@{t * 1e3:.2f}ms"
    elif t > 1e-6:
        return f"{N}@{t * 1e6:.2f}us"
    else:
        return f"{N}@{t * 1e9:.2f}ns"


def main():
    N = 1000
    cases = [
        ("(x+x+)+y", "xxxxxxxxxxxxxxxxxxxx"),
        (r"\w+@\w+\.\w+", "info@bitstamp.net"),
        (r"\w+@\w+\.\w+", "info@bitstampnet"),
        (
            "(a|b|asdf|opuj|sdjkfhg|jsdhf|dj|kdfs|as|p|d|ads|dsf|adsf|fds|fds|g|sdf|asdf|h)",
            "x" * 1000,
        ),
    ]
    for regex, text in cases:
        print(
            f"Regext: {fmt_bench(*bench_test(regex, text, N, 1))} for '{regex[:20]}' on '{text[:50]}': "
        )
        print(
            f"    Re: {fmt_bench(*bench_test_re(regex, text, N, 1))} for '{regex[:20]}' on '{text[:50]}': "
        )


if __name__ == "__main__":
    main()
