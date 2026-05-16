"""
test_program.py
CSC506 Module 5 Critical Thinking Assignment
Comprehensive Test Suite — Hash Table & Priority Queue
Author: Stacey
"""

import time
import random
from hash_table   import (HashTable, build_id_table, build_event_table,
                           build_location_table, linear_search_by_event,
                           linear_search_by_id, run_performance_comparison,
                           USER_STORIES)
from priority_queue import PriorityQueue


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

PASS = "PASS ✓"
FAIL = "FAIL ✗"

def check(condition, label):
    status = PASS if condition else FAIL
    print(f"   [{status}] {label}")
    return condition

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ─────────────────────────────────────────────
#  TEST 1: HASH TABLE — INSERT
# ─────────────────────────────────────────────

def test_hash_insert():
    section("TEST 1: Hash Table — Insert")
    ht = HashTable()

    # Basic insert
    ht.insert("US001", {"age": 34, "event": "job loss"})
    check(ht.size == 1, "Size = 1 after first insert")

    # Duplicate key update (not a new insert)
    ht.insert("US001", {"age": 34, "event": "job loss UPDATED"})
    check(ht.size == 1, "Size still 1 after duplicate key insert (update)")
    check(ht.search("US001")["event"] == "job loss UPDATED",
          "Value updated for duplicate key")

    # Multiple inserts (US001 already exists, so inserting USER_STORIES[:50]
    # updates US001 and adds 49 new = 50 total)
    for story in USER_STORIES[:50]:
        ht.insert(story["id"], story)
    check(ht.size == 50, "Size = 50 after inserting USER_STORIES[:50] (US001 updated)")

    # Full dataset
    ht2 = build_id_table(USER_STORIES)
    check(ht2.size == len(USER_STORIES), f"Full dataset: {ht2.size} items stored")


# ─────────────────────────────────────────────
#  TEST 2: HASH TABLE — SEARCH
# ─────────────────────────────────────────────

def test_hash_search():
    section("TEST 2: Hash Table — Search")
    ht = build_id_table(USER_STORIES)

    # Known existing key
    result = ht.search("US055")
    check(result is not None,           "Search US055 — found")
    check(result["location"] == "Phoenix, AZ",
                                        "Search US055 — correct location")

    # First and last story
    check(ht.search("US001") is not None, "Search US001 (first)")
    check(ht.search("US110") is not None, "Search US110 (last)")

    # Non-existent key
    check(ht.search("US999") is None,   "Search US999 — correctly returns None")

    # Event-table search
    et = build_event_table(USER_STORIES)
    recovery = et.search("addiction recovery")
    check(recovery is not None,         "Event search 'addiction recovery' found")
    check(len(recovery) >= 5,           f"Found {len(recovery)} recovery stories (≥5 expected)")

    # Location-table search
    lt = build_location_table(USER_STORIES)
    atlanta = lt.search("Atlanta, GA")
    check(atlanta is not None,          "Location search 'Atlanta, GA' found")
    check(len(atlanta) >= 4,            f"Found {len(atlanta)} Atlanta stories (≥4 expected)")


# ─────────────────────────────────────────────
#  TEST 3: HASH TABLE — DELETE
# ─────────────────────────────────────────────

def test_hash_delete():
    section("TEST 3: Hash Table — Delete")
    ht = build_id_table(USER_STORIES)
    original_size = ht.size

    # Delete existing key
    result = ht.delete("US001")
    check(result is True,                           "Delete US001 returns True")
    check(ht.size == original_size - 1,             "Size decremented after delete")
    check(ht.search("US001") is None,               "Deleted key no longer searchable")

    # Delete middle of chain (collision scenario)
    ht.delete("US055")
    check(ht.search("US055") is None,               "Mid-chain delete works")

    # Delete non-existent key
    result = ht.delete("US999")
    check(result is False,                          "Delete non-existent key returns False")
    check(ht.size == original_size - 2,             "Size unchanged after failed delete")

    # Delete all items
    ht_small = HashTable()
    for s in USER_STORIES[:10]:
        ht_small.insert(s["id"], s)
    for s in USER_STORIES[:10]:
        ht_small.delete(s["id"])
    check(ht_small.size == 0,                       "Table empty after deleting all items")


# ─────────────────────────────────────────────
#  TEST 4: COLLISION HANDLING
# ─────────────────────────────────────────────

def test_collision_handling():
    section("TEST 4: Collision Handling (Chaining)")

    # Force collisions with tiny table
    ht = HashTable()
    ht.TABLE_SIZE = 5
    ht.buckets    = [None] * 5

    keys = ["alpha", "beta", "gamma", "delta", "epsilon",
            "zeta", "eta", "theta", "iota", "kappa"]
    for k in keys:
        ht.insert(k, k.upper())

    check(ht.collisions > 0,               f"Collisions detected: {ht.collisions}")
    check(ht.size == 10,                   "All 10 items stored despite collisions")

    # All items retrievable
    all_found = all(ht.search(k) == k.upper() for k in keys)
    check(all_found,                       "All collided items retrievable")

    # Delete item in collision chain
    ht.delete("alpha")
    check(ht.search("alpha") is None,      "Delete from collision chain — gone")
    check(ht.search("beta") == "BETA",     "Delete from chain — neighbor intact")


# ─────────────────────────────────────────────
#  TEST 5: PRIORITY QUEUE — INSERT & PEEK
# ─────────────────────────────────────────────

def test_pq_insert_peek():
    section("TEST 5: Priority Queue — Insert & Peek")
    pq = PriorityQueue()

    check(pq.is_empty(),                   "Fresh queue is empty")

    pq.push(USER_STORIES[0])              # impact_score varies
    check(not pq.is_empty(),               "Not empty after first push")
    check(len(pq) == 1,                    "Length = 1 after one push")

    # Push 20 stories
    for s in USER_STORIES[:20]:
        pq.push(s)
    check(len(pq) == 21,                   "Length = 21 after 20 more pushes (+ original)")

    # Peek returns highest score
    priority, story = pq.peek()
    max_score = max(s["impact_score"] for s in USER_STORIES[:20] + [USER_STORIES[0]])
    check(priority == max_score,           f"Peek returns highest priority {priority} == {max_score}")
    check(len(pq) == 21,                   "Peek doesn't remove — length unchanged")


# ─────────────────────────────────────────────
#  TEST 6: PRIORITY QUEUE — EXTRACT-MAX
# ─────────────────────────────────────────────

def test_pq_extract():
    section("TEST 6: Priority Queue — Extract-Max")
    pq = PriorityQueue()
    pq.build_from_list(USER_STORIES)

    # Extract all and check descending order
    prev_priority = float("inf")
    order_valid   = True
    extracted     = []
    while not pq.is_empty():
        pri, story = pq.extract_max()
        if pri > prev_priority:
            order_valid = False
        prev_priority = pri
        extracted.append(pri)

    check(order_valid,                     "Extractions in non-increasing priority order")
    check(len(extracted) == len(USER_STORIES),
                                           f"All {len(extracted)} items extracted")
    check(pq.is_empty(),                   "Queue empty after extracting all")


# ─────────────────────────────────────────────
#  TEST 7: PRIORITY QUEUE — DELETE ARBITRARY
# ─────────────────────────────────────────────

def test_pq_delete():
    section("TEST 7: Priority Queue — Delete by ID")
    pq = PriorityQueue()
    pq.build_from_list(USER_STORIES)
    original_len = len(pq)

    # Delete middle item
    found = pq.delete_by_id("US050")
    check(found is True,                   "Delete US050 returns True")
    check(len(pq) == original_len - 1,     "Length decremented after delete")
    check(pq.search("US050") is None,      "Deleted story no longer searchable")

    # Heap property still valid after delete
    heap = pq._heap
    violations = 0
    for i in range(1, len(heap)):
        parent = (i - 1) // 2
        if heap[i][0] > heap[parent][0]:
            violations += 1
    check(violations == 0,                 f"Heap property preserved ({violations} violations)")

    # Delete non-existent
    found = pq.delete_by_id("US999")
    check(found is False,                  "Delete non-existent ID returns False")


# ─────────────────────────────────────────────
#  TEST 8: HEAP PROPERTY VALIDATION
# ─────────────────────────────────────────────

def test_heap_property():
    section("TEST 8: Heap Property — All 110 Items")
    pq = PriorityQueue()
    pq.build_from_list(USER_STORIES)

    heap       = pq._heap
    violations = 0
    for i in range(1, len(heap)):
        parent = (i - 1) // 2
        if heap[i][0] > heap[parent][0]:
            violations += 1

    check(violations == 0,                 f"Zero violations for {len(heap)}-item heap")

    # After random inserts
    pq2 = PriorityQueue()
    shuffled = USER_STORIES[:]
    random.shuffle(shuffled)
    for s in shuffled:
        pq2.push(s)

    heap2      = pq2._heap
    violations2 = sum(1 for i in range(1, len(heap2))
                      if heap2[i][0] > heap2[(i-1)//2][0])
    check(violations2 == 0,                "Heap property holds after shuffled inserts")


# ─────────────────────────────────────────────
#  TEST 9: PERFORMANCE COMPARISON
# ─────────────────────────────────────────────

def test_performance():
    section("TEST 9: Performance Comparison")
    results = run_performance_comparison(USER_STORIES, iterations=5_000)

    check(results["hash_id_ms"] < results["linear_id_ms"],
          f"Hash ID search faster: {results['hash_id_ms']:.3f} ms < {results['linear_id_ms']:.3f} ms")
    check(results["hash_ev_ms"] < results["linear_ev_ms"],
          f"Hash event search faster: {results['hash_ev_ms']:.3f} ms < {results['linear_ev_ms']:.3f} ms")


# ─────────────────────────────────────────────
#  TEST 10: EDGE CASES
# ─────────────────────────────────────────────

def test_edge_cases():
    section("TEST 10: Edge Cases & Error Handling")

    # Empty hash table operations
    ht = HashTable()
    check(ht.search("anything") is None,   "Search on empty table returns None")
    check(ht.delete("anything") is False,  "Delete on empty table returns False")

    # Empty priority queue
    pq = PriorityQueue()
    try:
        pq.peek()
        check(False,                       "Peek on empty queue should raise IndexError")
    except IndexError:
        check(True,                        "Peek on empty queue raises IndexError correctly")

    try:
        pq.extract_max()
        check(False,                       "Extract on empty queue should raise IndexError")
    except IndexError:
        check(True,                        "Extract on empty queue raises IndexError correctly")

    # Special characters in key
    ht2 = HashTable()
    ht2.insert("key with spaces", "val1")
    ht2.insert("key/with/slashes", "val2")
    ht2.insert("", "empty_key_val")
    check(ht2.search("key with spaces") == "val1",    "Key with spaces works")
    check(ht2.search("key/with/slashes") == "val2",   "Key with slashes works")
    check(ht2.search("") == "empty_key_val",          "Empty string key works")

    # Single-item priority queue
    pq2 = PriorityQueue()
    pq2.push(USER_STORIES[0])
    pri, s = pq2.extract_max()
    check(pq2.is_empty(),                  "Single-item extract leaves empty queue")


# ─────────────────────────────────────────────
#  SUMMARY REPORT
# ─────────────────────────────────────────────

def print_summary():
    section("DATASET SUMMARY")
    events   = {}
    locations = {}
    for s in USER_STORIES:
        events[s["major_event"]]    = events.get(s["major_event"], 0) + 1
        locations[s["location"]]    = locations.get(s["location"], 0) + 1

    print(f"\n  Total stories: {len(USER_STORIES)}")
    print(f"\n  Top event types:")
    for ev, count in sorted(events.items(), key=lambda x: -x[1])[:6]:
        bar = "█" * count
        print(f"    {ev:<25} {bar} ({count})")

    print(f"\n  Top locations:")
    for loc, count in sorted(locations.items(), key=lambda x: -x[1])[:6]:
        bar = "█" * count
        print(f"    {loc:<22} {bar} ({count})")

    age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-60": 0}
    for s in USER_STORIES:
        age = s["age"]
        if 18 <= age <= 25:   age_groups["18-25"] += 1
        elif 26 <= age <= 35: age_groups["26-35"] += 1
        elif 36 <= age <= 45: age_groups["36-45"] += 1
        else:                  age_groups["46-60"] += 1

    print(f"\n  Age distribution:")
    for grp, count in age_groups.items():
        bar = "█" * count
        print(f"    {grp:<10} {bar} ({count})")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "★"*60)
    print("  CSC506 MODULE 5 — FULL TEST SUITE")
    print("  Hash Table + Priority Queue")
    print("  Dataset: 110 Anonymous Life-Change User Stories")
    print("★"*60)

    tests = [
        test_hash_insert,
        test_hash_search,
        test_hash_delete,
        test_collision_handling,
        test_pq_insert_peek,
        test_pq_extract,
        test_pq_delete,
        test_heap_property,
        test_performance,
        test_edge_cases,
    ]

    pass_count = 0
    fail_count = 0

    for test_fn in tests:
        test_fn()

    print_summary()

    print("\n" + "★"*60)
    print("  All tests completed.")
    print("  Review output above for PASS/FAIL details.")
    print("★"*60 + "\n")
