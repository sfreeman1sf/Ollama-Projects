"""
priority_queue.py
CSC506 Module 5 Critical Thinking Assignment
Priority Queue Implementation using Binary Max-Heap
Dataset: Anonymous Life-Change User Stories (prioritized by impact_score)
Author: Stacey
"""

from hash_table import USER_STORIES   # Reuse the same dataset


# ─────────────────────────────────────────────
#  PRIORITY QUEUE — BINARY MAX-HEAP
# ─────────────────────────────────────────────

class PriorityQueue:
    """
    Binary Max-Heap Priority Queue.

    Heap Property (Max-Heap):
        Every parent node's priority >= its children's priority.
        Root is always the item with the HIGHEST priority.

    Internal storage: 0-indexed array (list).
        For node at index i:
            parent      = (i - 1) // 2
            left child  = 2*i + 1
            right child = 2*i + 2

    Complexities:
        insert (push)        : O(log n)  — sift up
        extract_max (pop)    : O(log n)  — sift down
        peek                 : O(1)      — root is always max
        search by value      : O(n)      — heap is not sorted
        delete arbitrary     : O(log n)  — find + replace + sift
        build from list      : O(n)      — Floyd's algorithm

    Priority field:
        We use 'impact_score' (1-10) from each story.
        Higher impact = higher priority (max-heap).
        Ties broken by story ID (alphabetical, lower = higher priority).
    """

    def __init__(self):
        self._heap = []   # list of (priority, story_dict) tuples

    def __len__(self):
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    # ── Internal Helpers ───────────────────────────────────────────────
    def _parent(self, i):      return (i - 1) // 2
    def _left(self, i):        return 2 * i + 1
    def _right(self, i):       return 2 * i + 2
    def _has_parent(self, i):  return i > 0
    def _has_left(self, i):    return self._left(i) < len(self._heap)
    def _has_right(self, i):   return self._right(i) < len(self._heap)

    def _compare(self, i, j) -> bool:
        """Return True if heap[i] should be higher priority than heap[j]."""
        pi, si = self._heap[i]
        pj, sj = self._heap[j]
        if pi != pj:
            return pi > pj           # higher score = higher priority
        return si["id"] < sj["id"]  # tie-break by ID (lexicographic)

    def _swap(self, i, j):
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    # ── Sift Up (after insert) ─────────────────────────────────────────
    def _sift_up(self, i: int):
        """Bubble node up until heap property is satisfied."""
        while self._has_parent(i) and self._compare(i, self._parent(i)):
            parent = self._parent(i)
            self._swap(i, parent)
            i = parent

    # ── Sift Down (after extract) ──────────────────────────────────────
    def _sift_down(self, i: int):
        """Push node down until heap property is satisfied."""
        while self._has_left(i):
            larger = self._left(i)
            if self._has_right(i) and self._compare(self._right(i), larger):
                larger = self._right(i)
            if self._compare(i, larger):
                break                # already satisfies heap property
            self._swap(i, larger)
            i = larger

    # ── Public Interface ───────────────────────────────────────────────

    def push(self, story: dict, priority: int = None) -> None:
        """
        Insert a story into the priority queue.
        Priority defaults to story's impact_score.
        O(log n)
        """
        if priority is None:
            priority = story.get("impact_score", 0)
        self._heap.append((priority, story))
        self._sift_up(len(self._heap) - 1)

    def peek(self):
        """
        Return (priority, story) of highest-priority item WITHOUT removing.
        O(1)
        """
        if self.is_empty():
            raise IndexError("Priority queue is empty.")
        return self._heap[0]

    def extract_max(self):
        """
        Remove and return (priority, story) with highest priority.
        O(log n)
        """
        if self.is_empty():
            raise IndexError("Priority queue is empty.")
        if len(self._heap) == 1:
            return self._heap.pop()

        # Swap root with last element, remove last, sift down root
        self._swap(0, len(self._heap) - 1)
        item = self._heap.pop()
        self._sift_down(0)
        return item

    def delete_by_id(self, story_id: str) -> bool:
        """
        Delete a story by ID.
        Find it (O(n)), replace with last, sift up or down. O(log n) after find.
        """
        for i, (_, story) in enumerate(self._heap):
            if story["id"] == story_id:
                if i == len(self._heap) - 1:
                    self._heap.pop()
                    return True
                self._heap[i] = self._heap.pop()   # replace with last
                self._sift_up(i)
                self._sift_down(i)
                return True
        return False

    def build_from_list(self, stories: list) -> None:
        """
        Build heap from a list of stories in O(n) using Floyd's algorithm
        (heapify). Faster than inserting one by one O(n log n).
        """
        self._heap = [(s.get("impact_score", 0), s) for s in stories]
        # Start from last non-leaf and sift down each node
        start = (len(self._heap) - 2) // 2
        for i in range(start, -1, -1):
            self._sift_down(i)

    def search(self, story_id: str):
        """Linear search O(n) — heap is not sorted beyond root."""
        for priority, story in self._heap:
            if story["id"] == story_id:
                return priority, story
        return None

    def to_sorted_list(self) -> list:
        """
        Extract all items in priority order (descending).
        Destructive — empties the queue. O(n log n).
        """
        result = []
        while not self.is_empty():
            result.append(self.extract_max())
        return result

    def display_heap_array(self, limit: int = 15):
        """Show internal array representation."""
        print(f"\n  Internal heap array (first {limit} entries):")
        for i, (priority, story) in enumerate(self._heap[:limit]):
            level = 0
            pos   = i + 1
            while pos > 1:
                pos //= 2
                level += 1
            indent = "  " * level
            print(f"  [{i:>3}] {indent}Priority={priority} | "
                  f"{story['id']} | {story['major_event'][:25]:<25} | {story['outcome'][:25]}")
        if len(self._heap) > limit:
            print(f"  ... ({len(self._heap) - limit} more items)")


# ─────────────────────────────────────────────
#  DEMO DRIVER
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import time

    print("\n" + "★"*60)
    print("  PRIORITY QUEUE DEMO — Life-Change User Stories")
    print("  Priority = impact_score (1-10, 10 = highest impact)")
    print("★"*60)

    # ── 1. Build heap from all 110 stories ────────────────────────────
    print("\n── BUILD: Floyd's O(n) heapify from 110 stories ─────────")
    pq = PriorityQueue()
    start = time.perf_counter()
    pq.build_from_list(USER_STORIES)
    build_time = time.perf_counter() - start
    print(f"   Heap built in {build_time*1000:.4f} ms")
    print(f"   Total items : {len(pq)}")

    # ── 2. Peek ───────────────────────────────────────────────────────
    print("\n── PEEK: Highest-impact story (no removal) ───────────────")
    priority, top_story = pq.peek()
    print(f"   Priority    : {priority}")
    print(f"   Story ID    : {top_story['id']}")
    print(f"   Location    : {top_story['location']}")
    print(f"   Major Event : {top_story['major_event']}")
    print(f"   Outcome     : {top_story['outcome']}")
    print(f"   Queue size  : {len(pq)} (unchanged)")

    # ── 3. Insert ─────────────────────────────────────────────────────
    print("\n── INSERT: Adding a priority-10 new story ────────────────")
    new_story = {
        "id": "US111", "age": 29, "location": "Atlanta, GA",
        "major_event": "homelessness", "outcome": "founded housing nonprofit",
        "years_ago": 2, "impact_score": 10
    }
    pq.push(new_story)
    print(f"   Inserted US111 | Queue size: {len(pq)}")
    p, s = pq.peek()
    print(f"   New peek: {s['id']} (Priority {p})")

    # ── 4. Extract-Max (top 5) ────────────────────────────────────────
    print("\n── EXTRACT-MAX: Top 5 highest-impact stories ─────────────")
    temp_pq = PriorityQueue()
    temp_pq.build_from_list(USER_STORIES)
    print(f"   {'Rank':<5} {'Priority':<10} {'ID':<8} {'Location':<22} "
          f"{'Major Event':<22} {'Outcome'}")
    print(f"   {'-'*100}")
    for rank in range(1, 6):
        pri, story = temp_pq.extract_max()
        print(f"   {rank:<5} {pri:<10} {story['id']:<8} {story['location']:<22} "
              f"{story['major_event']:<22} {story['outcome']}")

    # ── 5. Delete arbitrary ───────────────────────────────────────────
    print("\n── DELETE: Remove US070 by ID ────────────────────────────")
    print(f"   Size before: {len(pq)}")
    found = pq.delete_by_id("US070")
    print(f"   Delete US070 → Success: {found}")
    print(f"   Size after : {len(pq)}")
    print(f"   Verify gone: {pq.search('US070')}")

    # ── 6. Display heap array ─────────────────────────────────────────
    print("\n── INTERNAL HEAP ARRAY (first 10 nodes) ─────────────────")
    pq2 = PriorityQueue()
    pq2.build_from_list(USER_STORIES)
    pq2.display_heap_array(limit=10)

    # ── 7. Heap property verification ────────────────────────────────
    print("\n── HEAP PROPERTY VERIFICATION ────────────────────────────")
    heap = pq2._heap
    violations = 0
    for i in range(1, len(heap)):
        parent = (i - 1) // 2
        if heap[i][0] > heap[parent][0]:
            violations += 1
    print(f"   Items in heap      : {len(heap)}")
    print(f"   Property violations: {violations}  ({'PASS ✓' if violations == 0 else 'FAIL ✗'})")

    # ── 8. Priority queue — insert-then-extract timing ────────────────
    print("\n── PERFORMANCE: Insert + Extract on growing dataset ──────")
    import random
    for n in [10, 50, 110]:
        sample = USER_STORIES[:n]
        pq_test = PriorityQueue()

        start = time.perf_counter()
        for s in sample:
            pq_test.push(s)
        insert_time = time.perf_counter() - start

        start = time.perf_counter()
        while not pq_test.is_empty():
            pq_test.extract_max()
        extract_time = time.perf_counter() - start

        print(f"   n={n:<4} | Insert: {insert_time*1000:.4f} ms | "
              f"Extract-all: {extract_time*1000:.4f} ms")

    print("\nPriority queue demo complete.")
