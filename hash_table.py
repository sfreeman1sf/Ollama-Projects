"""
hash_table.py
CSC506 Module 5 Critical Thinking Assignment
Hash Table Implementation with Chaining Collision Handling
Dataset: Anonymous Life-Change User Stories
Author: Stacey
"""

import time
import hashlib


# ─────────────────────────────────────────────
#  ANONYMOUS USER STORY DATA (110 records)
# ─────────────────────────────────────────────

USER_STORIES = [
    {"id": "US001", "age": 34, "location": "Atlanta, GA",      "major_event": "job loss",          "outcome": "started business",      "years_ago": 3,  "impact_score": 9},
    {"id": "US002", "age": 22, "location": "Detroit, MI",      "major_event": "addiction recovery", "outcome": "sobriety + college",    "years_ago": 2,  "impact_score": 10},
    {"id": "US003", "age": 45, "location": "Houston, TX",      "major_event": "divorce",            "outcome": "found faith community", "years_ago": 5,  "impact_score": 8},
    {"id": "US004", "age": 28, "location": "Chicago, IL",      "major_event": "incarceration",      "outcome": "re-entry advocate",     "years_ago": 4,  "impact_score": 10},
    {"id": "US005", "age": 19, "location": "Memphis, TN",      "major_event": "homelessness",       "outcome": "housing + job",         "years_ago": 1,  "impact_score": 9},
    {"id": "US006", "age": 52, "location": "Baltimore, MD",    "major_event": "health crisis",      "outcome": "lifestyle overhaul",    "years_ago": 6,  "impact_score": 7},
    {"id": "US007", "age": 31, "location": "Phoenix, AZ",      "major_event": "domestic violence",  "outcome": "safe housing + healing","years_ago": 3,  "impact_score": 10},
    {"id": "US008", "age": 40, "location": "Cleveland, OH",    "major_event": "layoff",             "outcome": "career pivot to tech",  "years_ago": 2,  "impact_score": 8},
    {"id": "US009", "age": 25, "location": "New Orleans, LA",  "major_event": "natural disaster",   "outcome": "community rebuilding",  "years_ago": 5,  "impact_score": 9},
    {"id": "US010", "age": 37, "location": "Seattle, WA",      "major_event": "mental health",      "outcome": "therapy + stability",   "years_ago": 2,  "impact_score": 8},
    {"id": "US011", "age": 29, "location": "Denver, CO",       "major_event": "addiction recovery", "outcome": "wellness coaching",     "years_ago": 3,  "impact_score": 9},
    {"id": "US012", "age": 44, "location": "Miami, FL",        "major_event": "bankruptcy",         "outcome": "financial literacy",    "years_ago": 4,  "impact_score": 7},
    {"id": "US013", "age": 21, "location": "Atlanta, GA",      "major_event": "teen pregnancy",     "outcome": "nursing degree",        "years_ago": 3,  "impact_score": 9},
    {"id": "US014", "age": 55, "location": "Dallas, TX",       "major_event": "retirement crisis",  "outcome": "encore career",         "years_ago": 2,  "impact_score": 7},
    {"id": "US015", "age": 33, "location": "Philadelphia, PA", "major_event": "grief / loss",       "outcome": "grief counselor",       "years_ago": 5,  "impact_score": 9},
    {"id": "US016", "age": 27, "location": "Boston, MA",       "major_event": "job loss",           "outcome": "entrepreneur",          "years_ago": 1,  "impact_score": 8},
    {"id": "US017", "age": 48, "location": "Detroit, MI",      "major_event": "incarceration",      "outcome": "youth mentor",          "years_ago": 7,  "impact_score": 10},
    {"id": "US018", "age": 23, "location": "Houston, TX",      "major_event": "immigration",        "outcome": "citizenship + degree",  "years_ago": 4,  "impact_score": 9},
    {"id": "US019", "age": 36, "location": "Chicago, IL",      "major_event": "mental health",      "outcome": "public speaker",        "years_ago": 3,  "impact_score": 8},
    {"id": "US020", "age": 42, "location": "Los Angeles, CA",  "major_event": "divorce",            "outcome": "single parent success", "years_ago": 6,  "impact_score": 8},
    {"id": "US021", "age": 30, "location": "Memphis, TN",      "major_event": "addiction recovery", "outcome": "pastor / chaplain",     "years_ago": 5,  "impact_score": 10},
    {"id": "US022", "age": 26, "location": "Baltimore, MD",    "major_event": "homelessness",       "outcome": "social worker",         "years_ago": 2,  "impact_score": 9},
    {"id": "US023", "age": 50, "location": "Phoenix, AZ",      "major_event": "health crisis",      "outcome": "nutrition advocate",    "years_ago": 3,  "impact_score": 7},
    {"id": "US024", "age": 18, "location": "Cleveland, OH",    "major_event": "foster care aging",  "outcome": "college scholarship",   "years_ago": 1,  "impact_score": 9},
    {"id": "US025", "age": 39, "location": "New Orleans, LA",  "major_event": "domestic violence",  "outcome": "women's shelter work",  "years_ago": 4,  "impact_score": 10},
    {"id": "US026", "age": 43, "location": "Seattle, WA",      "major_event": "layoff",             "outcome": "nonprofit founder",     "years_ago": 2,  "impact_score": 8},
    {"id": "US027", "age": 24, "location": "Denver, CO",       "major_event": "mental health",      "outcome": "peer support cert.",    "years_ago": 1,  "impact_score": 7},
    {"id": "US028", "age": 35, "location": "Miami, FL",        "major_event": "natural disaster",   "outcome": "disaster relief org",   "years_ago": 3,  "impact_score": 9},
    {"id": "US029", "age": 47, "location": "Atlanta, GA",      "major_event": "grief / loss",       "outcome": "hospice volunteer",     "years_ago": 6,  "impact_score": 8},
    {"id": "US030", "age": 20, "location": "Dallas, TX",       "major_event": "incarceration",      "outcome": "GED + trade cert.",     "years_ago": 1,  "impact_score": 9},
    {"id": "US031", "age": 38, "location": "Philadelphia, PA", "major_event": "job loss",           "outcome": "IT career switch",      "years_ago": 2,  "impact_score": 8},
    {"id": "US032", "age": 53, "location": "Boston, MA",       "major_event": "divorce",            "outcome": "author / life coach",   "years_ago": 5,  "impact_score": 7},
    {"id": "US033", "age": 32, "location": "Detroit, MI",      "major_event": "addiction recovery", "outcome": "recovery house founder","years_ago": 4,  "impact_score": 10},
    {"id": "US034", "age": 41, "location": "Houston, TX",      "major_event": "immigration",        "outcome": "small biz owner",       "years_ago": 7,  "impact_score": 8},
    {"id": "US035", "age": 22, "location": "Chicago, IL",      "major_event": "homelessness",       "outcome": "stable housing + job",  "years_ago": 2,  "impact_score": 9},
    {"id": "US036", "age": 46, "location": "Los Angeles, CA",  "major_event": "health crisis",      "outcome": "fitness trainer",       "years_ago": 3,  "impact_score": 7},
    {"id": "US037", "age": 29, "location": "Memphis, TN",      "major_event": "domestic violence",  "outcome": "law enforcement career","years_ago": 4,  "impact_score": 9},
    {"id": "US038", "age": 56, "location": "Baltimore, MD",    "major_event": "mental health",      "outcome": "retired peacefully",    "years_ago": 8,  "impact_score": 7},
    {"id": "US039", "age": 25, "location": "Phoenix, AZ",      "major_event": "teen pregnancy",     "outcome": "family therapist",      "years_ago": 3,  "impact_score": 8},
    {"id": "US040", "age": 34, "location": "Cleveland, OH",    "major_event": "bankruptcy",         "outcome": "real estate investor",  "years_ago": 5,  "impact_score": 8},
    {"id": "US041", "age": 27, "location": "New Orleans, LA",  "major_event": "job loss",           "outcome": "culinary school",       "years_ago": 2,  "impact_score": 7},
    {"id": "US042", "age": 49, "location": "Seattle, WA",      "major_event": "grief / loss",       "outcome": "mental health advocate","years_ago": 6,  "impact_score": 9},
    {"id": "US043", "age": 21, "location": "Denver, CO",       "major_event": "incarceration",      "outcome": "legal reform activist", "years_ago": 1,  "impact_score": 10},
    {"id": "US044", "age": 60, "location": "Miami, FL",        "major_event": "health crisis",      "outcome": "community health ed",   "years_ago": 4,  "impact_score": 7},
    {"id": "US045", "age": 31, "location": "Atlanta, GA",      "major_event": "addiction recovery", "outcome": "social media ministry", "years_ago": 2,  "impact_score": 9},
    {"id": "US046", "age": 37, "location": "Dallas, TX",       "major_event": "natural disaster",   "outcome": "emergency management",  "years_ago": 3,  "impact_score": 8},
    {"id": "US047", "age": 43, "location": "Philadelphia, PA", "major_event": "domestic violence",  "outcome": "educator + advocate",   "years_ago": 5,  "impact_score": 10},
    {"id": "US048", "age": 19, "location": "Boston, MA",       "major_event": "homelessness",       "outcome": "college + dorm",        "years_ago": 1,  "impact_score": 9},
    {"id": "US049", "age": 36, "location": "Detroit, MI",      "major_event": "layoff",             "outcome": "unionized again",       "years_ago": 2,  "impact_score": 7},
    {"id": "US050", "age": 28, "location": "Houston, TX",      "major_event": "mental health",      "outcome": "artist + therapist",    "years_ago": 3,  "impact_score": 8},
    {"id": "US051", "age": 33, "location": "Chicago, IL",      "major_event": "divorce",            "outcome": "stronger co-parenting", "years_ago": 4,  "impact_score": 7},
    {"id": "US052", "age": 45, "location": "Los Angeles, CA",  "major_event": "addiction recovery", "outcome": "sober living home mgr", "years_ago": 6,  "impact_score": 10},
    {"id": "US053", "age": 24, "location": "Memphis, TN",      "major_event": "immigration",        "outcome": "DACA + scholarship",    "years_ago": 2,  "impact_score": 9},
    {"id": "US054", "age": 39, "location": "Baltimore, MD",    "major_event": "grief / loss",       "outcome": "suicide prevention wk", "years_ago": 5,  "impact_score": 10},
    {"id": "US055", "age": 26, "location": "Phoenix, AZ",      "major_event": "job loss",           "outcome": "freelance + remote",    "years_ago": 1,  "impact_score": 7},
    {"id": "US056", "age": 51, "location": "Cleveland, OH",    "major_event": "bankruptcy",         "outcome": "financial coach cert.", "years_ago": 3,  "impact_score": 8},
    {"id": "US057", "age": 23, "location": "New Orleans, LA",  "major_event": "incarceration",      "outcome": "music producer",        "years_ago": 2,  "impact_score": 9},
    {"id": "US058", "age": 47, "location": "Seattle, WA",      "major_event": "health crisis",      "outcome": "palliative care nurse", "years_ago": 4,  "impact_score": 8},
    {"id": "US059", "age": 30, "location": "Denver, CO",       "major_event": "domestic violence",  "outcome": "nonprofit law clinic",  "years_ago": 3,  "impact_score": 10},
    {"id": "US060", "age": 20, "location": "Miami, FL",        "major_event": "teen pregnancy",     "outcome": "community college",     "years_ago": 1,  "impact_score": 8},
    {"id": "US061", "age": 42, "location": "Atlanta, GA",      "major_event": "layoff",             "outcome": "data analytics cert.",  "years_ago": 2,  "impact_score": 8},
    {"id": "US062", "age": 35, "location": "Dallas, TX",       "major_event": "mental health",      "outcome": "DBT facilitator",       "years_ago": 3,  "impact_score": 8},
    {"id": "US063", "age": 57, "location": "Philadelphia, PA", "major_event": "divorce",            "outcome": "peace + solo travel",   "years_ago": 7,  "impact_score": 7},
    {"id": "US064", "age": 22, "location": "Boston, MA",       "major_event": "addiction recovery", "outcome": "NA group leader",       "years_ago": 1,  "impact_score": 9},
    {"id": "US065", "age": 40, "location": "Detroit, MI",      "major_event": "homelessness",       "outcome": "housing navigator",     "years_ago": 5,  "impact_score": 9},
    {"id": "US066", "age": 32, "location": "Houston, TX",      "major_event": "natural disaster",   "outcome": "FEMA volunteer",        "years_ago": 3,  "impact_score": 8},
    {"id": "US067", "age": 44, "location": "Chicago, IL",      "major_event": "grief / loss",       "outcome": "memorial garden proj.", "years_ago": 4,  "impact_score": 8},
    {"id": "US068", "age": 18, "location": "Los Angeles, CA",  "major_event": "foster care aging",  "outcome": "youth center director", "years_ago": 2,  "impact_score": 10},
    {"id": "US069", "age": 29, "location": "Memphis, TN",      "major_event": "job loss",           "outcome": "HVAC certification",    "years_ago": 1,  "impact_score": 7},
    {"id": "US070", "age": 38, "location": "Baltimore, MD",    "major_event": "incarceration",      "outcome": "paralegal + activist",  "years_ago": 6,  "impact_score": 10},
    {"id": "US071", "age": 54, "location": "Phoenix, AZ",      "major_event": "health crisis",      "outcome": "diabetes educator",     "years_ago": 5,  "impact_score": 7},
    {"id": "US072", "age": 25, "location": "Cleveland, OH",    "major_event": "mental health",      "outcome": "art therapy student",   "years_ago": 2,  "impact_score": 7},
    {"id": "US073", "age": 46, "location": "New Orleans, LA",  "major_event": "addiction recovery", "outcome": "restaurant owner",      "years_ago": 8,  "impact_score": 9},
    {"id": "US074", "age": 27, "location": "Seattle, WA",      "major_event": "domestic violence",  "outcome": "Title IX coordinator",  "years_ago": 3,  "impact_score": 10},
    {"id": "US075", "age": 50, "location": "Denver, CO",       "major_event": "layoff",             "outcome": "life coach + speaker",  "years_ago": 4,  "impact_score": 8},
    {"id": "US076", "age": 21, "location": "Miami, FL",        "major_event": "immigration",        "outcome": "interpreter + guide",   "years_ago": 1,  "impact_score": 8},
    {"id": "US077", "age": 34, "location": "Atlanta, GA",      "major_event": "bankruptcy",         "outcome": "credit union member",   "years_ago": 3,  "impact_score": 7},
    {"id": "US078", "age": 48, "location": "Dallas, TX",       "major_event": "grief / loss",       "outcome": "bereavement coord.",    "years_ago": 5,  "impact_score": 9},
    {"id": "US079", "age": 23, "location": "Philadelphia, PA", "major_event": "homelessness",       "outcome": "social services mgr.",  "years_ago": 2,  "impact_score": 9},
    {"id": "US080", "age": 41, "location": "Boston, MA",       "major_event": "job loss",           "outcome": "workforce dev. trainer","years_ago": 3,  "impact_score": 8},
    {"id": "US081", "age": 36, "location": "Detroit, MI",      "major_event": "teen pregnancy",     "outcome": "pediatric nurse",       "years_ago": 7,  "impact_score": 9},
    {"id": "US082", "age": 28, "location": "Houston, TX",      "major_event": "natural disaster",   "outcome": "environmental science", "years_ago": 2,  "impact_score": 8},
    {"id": "US083", "age": 55, "location": "Chicago, IL",      "major_event": "divorce",            "outcome": "mediator + counselor",  "years_ago": 9,  "impact_score": 7},
    {"id": "US084", "age": 19, "location": "Los Angeles, CA",  "major_event": "addiction recovery", "outcome": "youth outreach coord.", "years_ago": 1,  "impact_score": 9},
    {"id": "US085", "age": 43, "location": "Memphis, TN",      "major_event": "incarceration",      "outcome": "construction mgmt.",    "years_ago": 5,  "impact_score": 9},
    {"id": "US086", "age": 31, "location": "Baltimore, MD",    "major_event": "health crisis",      "outcome": "plant-based chef",      "years_ago": 2,  "impact_score": 7},
    {"id": "US087", "age": 26, "location": "Phoenix, AZ",      "major_event": "mental health",      "outcome": "school counselor",      "years_ago": 3,  "impact_score": 8},
    {"id": "US088", "age": 37, "location": "Cleveland, OH",    "major_event": "domestic violence",  "outcome": "detective + advocate",  "years_ago": 4,  "impact_score": 10},
    {"id": "US089", "age": 52, "location": "New Orleans, LA",  "major_event": "grief / loss",       "outcome": "community choir dir.",  "years_ago": 7,  "impact_score": 8},
    {"id": "US090", "age": 24, "location": "Seattle, WA",      "major_event": "foster care aging",  "outcome": "foster care reformer",  "years_ago": 2,  "impact_score": 10},
    {"id": "US091", "age": 33, "location": "Denver, CO",       "major_event": "job loss",           "outcome": "renewable energy tech", "years_ago": 1,  "impact_score": 8},
    {"id": "US092", "age": 45, "location": "Miami, FL",        "major_event": "immigration",        "outcome": "ESL teacher",           "years_ago": 6,  "impact_score": 8},
    {"id": "US093", "age": 20, "location": "Atlanta, GA",      "major_event": "homelessness",       "outcome": "HBCU full scholarship", "years_ago": 1,  "impact_score": 10},
    {"id": "US094", "age": 38, "location": "Dallas, TX",       "major_event": "addiction recovery", "outcome": "CrossFit coach",        "years_ago": 4,  "impact_score": 9},
    {"id": "US095", "age": 49, "location": "Philadelphia, PA", "major_event": "bankruptcy",         "outcome": "accountant retraining", "years_ago": 5,  "impact_score": 7},
    {"id": "US096", "age": 27, "location": "Boston, MA",       "major_event": "natural disaster",   "outcome": "urban planner",         "years_ago": 2,  "impact_score": 8},
    {"id": "US097", "age": 44, "location": "Detroit, MI",      "major_event": "layoff",             "outcome": "EV tech retraining",    "years_ago": 3,  "impact_score": 8},
    {"id": "US098", "age": 22, "location": "Houston, TX",      "major_event": "grief / loss",       "outcome": "pediatric chaplain",    "years_ago": 1,  "impact_score": 9},
    {"id": "US099", "age": 58, "location": "Chicago, IL",      "major_event": "health crisis",      "outcome": "patient advocate",      "years_ago": 8,  "impact_score": 7},
    {"id": "US100", "age": 30, "location": "Los Angeles, CA",  "major_event": "domestic violence",  "outcome": "film documentarian",    "years_ago": 3,  "impact_score": 10},
    {"id": "US101", "age": 35, "location": "Memphis, TN",      "major_event": "incarceration",      "outcome": "reentry housing org",   "years_ago": 4,  "impact_score": 10},
    {"id": "US102", "age": 41, "location": "Baltimore, MD",    "major_event": "teen pregnancy",     "outcome": "OB/GYN nurse",          "years_ago": 9,  "impact_score": 9},
    {"id": "US103", "age": 29, "location": "Phoenix, AZ",      "major_event": "addiction recovery", "outcome": "peer recovery coach",   "years_ago": 2,  "impact_score": 9},
    {"id": "US104", "age": 47, "location": "Cleveland, OH",    "major_event": "mental health",      "outcome": "yoga + mindfulness",    "years_ago": 5,  "impact_score": 7},
    {"id": "US105", "age": 23, "location": "New Orleans, LA",  "major_event": "homelessness",       "outcome": "tiny home builder",     "years_ago": 1,  "impact_score": 9},
    {"id": "US106", "age": 53, "location": "Seattle, WA",      "major_event": "job loss",           "outcome": "community college dean","years_ago": 6,  "impact_score": 8},
    {"id": "US107", "age": 26, "location": "Denver, CO",       "major_event": "grief / loss",       "outcome": "crisis text counselor", "years_ago": 2,  "impact_score": 9},
    {"id": "US108", "age": 40, "location": "Miami, FL",        "major_event": "domestic violence",  "outcome": "shelter director",      "years_ago": 5,  "impact_score": 10},
    {"id": "US109", "age": 19, "location": "Atlanta, GA",      "major_event": "foster care aging",  "outcome": "youth housing advocate","years_ago": 1,  "impact_score": 10},
    {"id": "US110", "age": 36, "location": "Dallas, TX",       "major_event": "natural disaster",   "outcome": "climate resilience eng","years_ago": 3,  "impact_score": 8},
]


# ─────────────────────────────────────────────
#  HASH TABLE IMPLEMENTATION (Chaining)
# ─────────────────────────────────────────────

class HashNode:
    """A single node in a linked list chain."""
    def __init__(self, key, value):
        self.key   = key
        self.value = value
        self.next  = None


class HashTable:
    """
    Hash table using separate chaining for collision resolution.

    Hash Function Design:
        Keys are strings like "US001", "Atlanta, GA", "addiction recovery".
        We convert each character to its ASCII value, multiply by a prime
        weight (31), and sum — a classic polynomial rolling hash.
        Modulo with table size (prime = 127) distributes buckets evenly.

        h(key) = (Σ ord(c) * 31^i) % TABLE_SIZE

    Why chaining?
        - Simple to implement and understand.
        - Handles load factors > 1 gracefully (lists can grow).
        - No clustering effect (vs. linear probing).
        - Deletion is straightforward — just unlink the node.
    """

    TABLE_SIZE = 127  # Prime number reduces clustering

    def __init__(self):
        self.buckets      = [None] * self.TABLE_SIZE
        self.size         = 0           # number of stored items
        self.collisions   = 0           # tracked for analysis

    # ── Hash Function ──────────────────────────────────────────────────
    def _hash(self, key: str) -> int:
        """Polynomial rolling hash — O(len(key))."""
        h = 0
        for ch in str(key):
            h = (h * 31 + ord(ch)) % self.TABLE_SIZE
        return h

    # ── Insert ─────────────────────────────────────────────────────────
    def insert(self, key: str, value) -> None:
        index = self._hash(key)
        node  = self.buckets[index]

        if node is not None:
            self.collisions += 1          # bucket already occupied

        # Walk chain — update if key exists
        while node:
            if node.key == key:
                node.value = value
                return
            node = node.next

        # Prepend new node (O(1))
        new_node          = HashNode(key, value)
        new_node.next     = self.buckets[index]
        self.buckets[index] = new_node
        self.size        += 1

    # ── Search ─────────────────────────────────────────────────────────
    def search(self, key: str):
        """Return value for key, or None if not found. O(1) average."""
        index = self._hash(key)
        node  = self.buckets[index]
        while node:
            if node.key == key:
                return node.value
            node = node.next
        return None

    # ── Delete ─────────────────────────────────────────────────────────
    def delete(self, key: str) -> bool:
        """Remove key from table. Returns True if found and removed."""
        index = self._hash(key)
        node  = self.buckets[index]
        prev  = None

        while node:
            if node.key == key:
                if prev:
                    prev.next = node.next
                else:
                    self.buckets[index] = node.next
                self.size -= 1
                return True
            prev, node = node, node.next
        return False

    # ── Utilities ──────────────────────────────────────────────────────
    def load_factor(self) -> float:
        return self.size / self.TABLE_SIZE

    def occupied_buckets(self) -> int:
        return sum(1 for b in self.buckets if b is not None)

    def display_stats(self):
        print(f"\n{'='*50}")
        print(f"  HASH TABLE STATS")
        print(f"{'='*50}")
        print(f"  Table size (buckets) : {self.TABLE_SIZE}")
        print(f"  Items stored         : {self.size}")
        print(f"  Occupied buckets     : {self.occupied_buckets()}")
        print(f"  Load factor          : {self.load_factor():.3f}")
        print(f"  Collisions detected  : {self.collisions}")
        print(f"{'='*50}\n")


# ─────────────────────────────────────────────
#  BUILD SEARCH-KEY HASH TABLE
#  Keys = "major_event" field  (matches Ollama pattern-search design)
#  Multiple stories per event type → chaining shines here
# ─────────────────────────────────────────────

def build_event_table(stories: list) -> HashTable:
    """
    Build a hash table keyed by major_event for fast pattern lookup.
    Stores a list of story IDs as the value so we can find all stories
    sharing the same event type in O(1) average time.
    """
    ht = HashTable()
    for story in stories:
        key = story["major_event"]
        existing = ht.search(key)
        if existing is None:
            ht.insert(key, [story])
        else:
            existing.append(story)
    return ht


def build_location_table(stories: list) -> HashTable:
    """Build a hash table keyed by location."""
    ht = HashTable()
    for story in stories:
        key = story["location"]
        existing = ht.search(key)
        if existing is None:
            ht.insert(key, [story])
        else:
            existing.append(story)
    return ht


def build_id_table(stories: list) -> HashTable:
    """Build a hash table keyed by story ID — direct O(1) lookup."""
    ht = HashTable()
    for story in stories:
        ht.insert(story["id"], story)
    return ht


# ─────────────────────────────────────────────
#  LINEAR SEARCH (for performance comparison)
# ─────────────────────────────────────────────

def linear_search_by_event(stories: list, target_event: str) -> list:
    """O(n) linear scan — compare against hash table search."""
    return [s for s in stories if s["major_event"] == target_event]


def linear_search_by_id(stories: list, target_id: str):
    """O(n) linear scan by ID."""
    for s in stories:
        if s["id"] == target_id:
            return s
    return None


# ─────────────────────────────────────────────
#  PERFORMANCE COMPARISON
# ─────────────────────────────────────────────

def run_performance_comparison(stories: list, iterations: int = 10_000):
    """Compare hash table vs linear search over many repeated lookups."""
    print("\n" + "="*60)
    print("  PERFORMANCE COMPARISON: Hash Table vs Linear Search")
    print("="*60)

    # Build structures once
    id_table    = build_id_table(stories)
    event_table = build_event_table(stories)

    test_ids    = ["US001", "US055", "US110"]
    test_events = ["addiction recovery", "domestic violence", "grief / loss"]

    # ── ID lookup (hash) ──────────────────────────────────────
    start = time.perf_counter()
    for _ in range(iterations):
        for tid in test_ids:
            id_table.search(tid)
    hash_id_time = time.perf_counter() - start

    # ── ID lookup (linear) ────────────────────────────────────
    start = time.perf_counter()
    for _ in range(iterations):
        for tid in test_ids:
            linear_search_by_id(stories, tid)
    linear_id_time = time.perf_counter() - start

    # ── Event lookup (hash) ───────────────────────────────────
    start = time.perf_counter()
    for _ in range(iterations):
        for ev in test_events:
            event_table.search(ev)
    hash_ev_time = time.perf_counter() - start

    # ── Event lookup (linear) ─────────────────────────────────
    start = time.perf_counter()
    for _ in range(iterations):
        for ev in test_events:
            linear_search_by_event(stories, ev)
    linear_ev_time = time.perf_counter() - start

    # ── Report ────────────────────────────────────────────────
    def speedup(linear, hashed):
        return linear / hashed if hashed > 0 else float("inf")

    print(f"\n  ID LOOKUP ({iterations:,} iterations × 3 keys)")
    print(f"    Hash Table : {hash_id_time*1000:.3f} ms")
    print(f"    Linear     : {linear_id_time*1000:.3f} ms")
    print(f"    Speedup    : {speedup(linear_id_time, hash_id_time):.1f}×")

    print(f"\n  EVENT LOOKUP ({iterations:,} iterations × 3 event types)")
    print(f"    Hash Table : {hash_ev_time*1000:.3f} ms")
    print(f"    Linear     : {linear_ev_time*1000:.3f} ms")
    print(f"    Speedup    : {speedup(linear_ev_time, hash_ev_time):.1f}×")
    print("="*60 + "\n")

    return {
        "hash_id_ms": hash_id_time * 1000,
        "linear_id_ms": linear_id_time * 1000,
        "hash_ev_ms": hash_ev_time * 1000,
        "linear_ev_ms": linear_ev_time * 1000,
    }


# ─────────────────────────────────────────────
#  DEMO DRIVER
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "★"*60)
    print("  HASH TABLE DEMO — Life-Change User Stories Dataset")
    print("★"*60)

    # 1. Build tables
    id_table    = build_id_table(USER_STORIES)
    event_table = build_event_table(USER_STORIES)
    loc_table   = build_location_table(USER_STORIES)

    id_table.display_stats()

    # 2. Insert demo
    print("── INSERT: Adding story US111 ──────────────────────────")
    id_table.insert("US111", {"id": "US111", "age": 44, "location": "Atlanta, GA",
                               "major_event": "addiction recovery",
                               "outcome": "social entrepreneur", "impact_score": 9})
    print(f"   Table size after insert: {id_table.size}")

    # 3. Search demo
    print("\n── SEARCH: Look up US055 ───────────────────────────────")
    result = id_table.search("US055")
    if result:
        print(f"   Found  → {result['id']} | {result['location']} | "
              f"{result['major_event']} → {result['outcome']}")

    print("\n── SEARCH: All 'addiction recovery' stories ────────────")
    recovery_stories = event_table.search("addiction recovery")
    if recovery_stories:
        print(f"   Found {len(recovery_stories)} stories tagged 'addiction recovery':")
        for s in recovery_stories[:5]:
            print(f"     {s['id']} | Age {s['age']} | {s['location']} → {s['outcome']}")
        if len(recovery_stories) > 5:
            print(f"     ... and {len(recovery_stories)-5} more")

    # 4. Delete demo
    print("\n── DELETE: Remove US001 ────────────────────────────────")
    success = id_table.delete("US001")
    print(f"   Delete successful: {success}")
    print(f"   Verify gone — search returns: {id_table.search('US001')}")

    # 5. Collision demo
    print("\n── COLLISION HANDLING DEMO ─────────────────────────────")
    ht_small = HashTable()
    ht_small.TABLE_SIZE = 7   # Tiny table forces collisions
    ht_small.buckets    = [None] * 7
    words = ["Atlanta", "Detroit", "Memphis", "Chicago", "Phoenix",
             "Houston", "Denver", "Miami", "Seattle", "Baltimore"]
    for w in words:
        ht_small.insert(w, True)
    print(f"   Inserted {len(words)} cities into size-7 table")
    print(f"   Collisions: {ht_small.collisions}")
    print(f"   Occupied buckets: {ht_small.occupied_buckets()} / 7")

    # 6. Performance comparison
    run_performance_comparison(USER_STORIES)

    print("Demo complete. See priority_queue.py for heap implementation.")
