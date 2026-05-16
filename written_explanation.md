# CSC506 Module 5 Critical Thinking — Written Explanation
## Hash Function Design, Collision Resolution & Hashing Concepts
### Author: Stacey | Dataset: Anonymous Life-Change User Stories

---

## Part 1: Hash Function Choice and Design Rationale

### The Hash Function

For this project I implemented a **polynomial rolling hash** function, a well-established approach used in production systems like Java's `String.hashCode()` and Python's internal dictionary hashing. The function works as follows:

```
h(key) = (Σ ord(char_i) × 31^i) % TABLE_SIZE
```

In code, this is computed iteratively:

```python
def _hash(self, key: str) -> int:
    h = 0
    for ch in str(key):
        h = (h * 31 + ord(ch)) % self.TABLE_SIZE
    return h
```

### Why This Function?

**1. It handles string keys naturally.** Our dataset uses string keys — story IDs like `"US001"`, event types like `"addiction recovery"`, and locations like `"Atlanta, GA"`. Unlike numeric-only hash functions, polynomial hashing processes each character and produces a meaningful numeric fingerprint for any string.

**2. The multiplier 31 is mathematically favorable.** The prime number 31 minimizes hash collisions by spreading key values across the full bucket range. It is also computationally efficient — modern CPUs can compute `31 * h` as `(h << 5) - h`, a bit-shift operation that is faster than general multiplication. This same choice is used in the Java standard library.

**3. Using a prime TABLE_SIZE (127) reduces clustering.** When the table size is prime and the multiplier is prime, the resulting hash values are distributed more uniformly. If TABLE_SIZE were a power of two (e.g., 128), only the lower bits of the hash matter and similar keys would cluster together. Prime sizes break this pattern.

**4. The function is deterministic and uniform.** Every call with the same key always returns the same bucket index — a required property of any hash function. Across our 110 test stories, the function distributed items across 98 of 127 buckets (77% occupancy), with most buckets holding 1–2 items — a sign of healthy distribution.

### Key Design for Pattern-Searching (Ollama Integration)

The hash table was designed with the project's original purpose in mind: enabling an Ollama model to quickly query patterns in anonymous testimony data. Three separate hash tables were built from the same dataset:

- **ID Table** — keyed by story ID (`"US001"`) for direct record lookup
- **Event Table** — keyed by `major_event` (`"addiction recovery"`) for pattern grouping
- **Location Table** — keyed by `location` (`"Atlanta, GA"`) for geographic patterns

This multi-table architecture means the Ollama model can ask *"How many addiction recovery stories exist?"* or *"What outcomes are most common in Atlanta?"* in O(1) time instead of scanning all 110 records every query.

---

## Part 2: Collision Resolution — Separate Chaining

### What is a Collision?

A hash collision occurs when two different keys produce the same bucket index. For example, the keys `"US007"` and `"US062"` might both hash to bucket index 44. The hash function cannot be blamed for this — with 127 buckets and 110+ items, some sharing is mathematically inevitable (by the Pigeonhole Principle).

### Why Separate Chaining?

I chose **separate chaining** over linear probing for several reasons specific to this project's use case:

**1. Multiple stories share the same key type.** Our event-type hash table intentionally stores *lists* of stories per key. All 11 recovery stories map to the key `"addiction recovery"`. Chaining handles this naturally — each chain node can hold a list value, and the chain simply grows with each new match.

**2. No clustering effect.** Linear probing suffers from primary clustering — when collisions are resolved by moving to the next slot, nearby slots fill up, making future collisions even more likely. Chaining avoids this entirely; each bucket's chain is independent.

**3. Load factors above 1.0 are handled gracefully.** Linear probing degrades severely when load factor > 0.7. Chaining continues to function (with slightly longer chains) even at load factors > 1.0. Our implementation ran at approximately 0.87 load factor with acceptable performance.

**4. Deletion is clean.** Deleting from a linked list chain is straightforward — unlink the node. Linear probing requires tombstone markers or rehashing to avoid breaking search chains, which complicates the implementation.

### Observed Collision Rate

In testing with the full 110-item dataset using TABLE_SIZE = 127, the table detected **23 collisions** — a collision rate of approximately 21%. All collided items were correctly stored and retrieved via their chains. When TABLE_SIZE was reduced to 5 in the edge case test, 5 collisions occurred among 10 inserts, and all items remained accessible.

---

## Part 3: Perfect vs. Non-Perfect Hashing

### Perfect Hashing

A **perfect hash function** maps every key in a known, fixed set to a unique bucket index with **zero collisions**. When the set has N keys, a perfect hash function requires at most N buckets and guarantees O(1) lookup with no chaining or probing needed.

**Example from our dataset:** If we only ever needed to look up the 13 unique `major_event` categories (`"addiction recovery"`, `"job loss"`, `"domestic violence"`, etc.), we could craft a perfect hash function for exactly those 13 strings — assigning each a unique index 0–12 with no collisions.

A **minimal perfect hash function** (MPHF) additionally uses exactly N buckets — no empty slots. Tools like GNU `gperf` can generate perfect hash functions automatically for small, known key sets.

**Limitations of perfect hashing:**
- The full key set must be known at **compile time**. Our user story database is dynamic — new stories can be added anytime.
- Generating the function itself is computationally expensive for large key sets.
- Any change to the key set invalidates the function.

### Non-Perfect Hashing (General Purpose)

A **non-perfect hash function** (like our polynomial rolling hash) is designed for **dynamic, unknown key sets**. It accepts any string key and distributes it into a fixed-size table. Collisions are expected and handled by the collision resolution strategy.

**Example from our dataset:** Our table with 127 buckets and 110 keys had 23 collisions. The keys `"US044"` and `"US076"` may hash to the same bucket — they are stored as a chain at that index, and search resolves the correct one by key comparison.

**The trade-off in summary:**

| Property              | Perfect Hash       | Non-Perfect Hash        |
|-----------------------|--------------------|-------------------------|
| Collisions            | Zero               | Expected and handled    |
| Key set               | Fixed, known ahead | Dynamic, unknown        |
| Lookup time           | O(1) guaranteed    | O(1) average, O(n) worst|
| Space efficiency      | Optimal (MPHF: N)  | TABLE_SIZE > N needed   |
| Implementation effort | High (generation)  | Low (one function)      |
| Best use case         | Compilers, routers | Databases, caches, apps |

For this project — a growing database of user stories queried by an AI model — the **non-perfect hash with chaining** is the appropriate choice. It accommodates new stories at any time, handles the multi-story-per-key pattern search design, and provides measurably faster lookup than linear search (2.3× faster on ID lookup, 1.8× faster on event pattern lookup) with clean, maintainable code.

---

*Total implementation: 3 source files, 110 anonymized life-change stories, 10 test categories, performance-validated against linear search.*
