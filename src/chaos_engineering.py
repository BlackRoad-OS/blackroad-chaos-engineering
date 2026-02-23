#!/usr/bin/env python3
"""BlackRoad Chaos Engineering — controlled fault injection for resilience testing."""
import random, time, os, json

class ChaosMonkey:
    def __init__(self, seed: int = None):
        random.seed(seed)
        self.log = []

    def inject_latency(self, fn, min_ms=50, max_ms=2000):
        """Wrap a function with random latency injection."""
        def wrapper(*args, **kwargs):
            delay = random.randint(min_ms, max_ms) / 1000
            time.sleep(delay)
            result = fn(*args, **kwargs)
            self.log.append({"type": "latency", "delay_ms": int(delay*1000), "fn": fn.__name__})
            return result
        return wrapper

    def inject_failure(self, fn, failure_rate=0.1):
        """Wrap a function with random failure injection."""
        def wrapper(*args, **kwargs):
            if random.random() < failure_rate:
                self.log.append({"type": "failure", "fn": fn.__name__})
                raise RuntimeError(f"Chaos: injected failure in {fn.__name__}")
            return fn(*args, **kwargs)
        return wrapper

    def report(self):
        failures = sum(1 for e in self.log if e["type"] == "failure")
        latencies = [e["delay_ms"] for e in self.log if e["type"] == "latency"]
        print(f"\\n🔥 Chaos Report")
        print(f"  Total events: {len(self.log)}")
        print(f"  Failures:     {failures}")
        if latencies:
            print(f"  Avg latency:  {sum(latencies)/len(latencies):.1f}ms")
            print(f"  Max latency:  {max(latencies)}ms")

if __name__ == "__main__":
    monkey = ChaosMonkey(42)

    @monkey.inject_latency
    @monkey.inject_failure
    def mock_api_call(payload: str) -> dict:
        return {"status": "ok", "payload": payload}

    for i in range(20):
        try: mock_api_call(f"request_{i}")
        except RuntimeError as e: print(f"  ⚡ {e}")
    monkey.report()

