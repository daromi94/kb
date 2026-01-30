# Bloom Filters

A Bloom filter is a space-efficient, probabilistic data structure for testing
set membership. It can tell you with certainty that something is **not** in a
set, but only that something is **probably** in the set.

## Core Trade-off

Storing a massive list (millions of malicious URLs) takes huge amounts of RAM.
A Bloom filter uses a tiny fraction of that space, but may occasionally report
false positives—saying a safe URL is malicious when it isn't. It will never
report false negatives—it will never say a malicious URL is safe.

## How It Works

A Bloom filter has two components:

1. **Bit array** - A row of bits, all initially set to 0
2. **Hash functions** - Multiple independent hash functions (e.g., 3)

**Insertion.** To add "Google":

1. Run "Google" through the 3 hash functions
2. They output positions 2, 5, and 8
3. Set bits at positions 2, 5, and 8 to 1

**Query.** To check if "Google" is in the set:

1. Run "Google" through the same hash functions → 2, 5, 8
2. Check if bits 2, 5, and 8 are all 1
3. If yes: "Google" is *probably* in the set

**Definite negative.** To check if "Apple" is in the set:

1. Hash functions return 2, 8, and 9
2. Bit 2 is 1, bit 8 is 1, but bit 9 is 0
3. "Apple" is **definitely not** in the set—if it were, bit 9 would be 1

## False Positives

Checking for "Yahoo" might return positions 2, 5, and 8—already set by
"Google". The filter returns true even though "Yahoo" was never inserted.

Making the bit array larger or using more hash functions reduces false positive
rates but cannot eliminate them entirely.

## Use Cases

Bloom filters serve as a first line of defense to avoid expensive operations.

**Databases (Cassandra, ScyllaDB, PostgreSQL).** Before checking disk for a row
(slow), check the Bloom filter. If it says "No," skip the disk read entirely.

**Web browsers.** Chrome used Bloom filters to check malicious URLs. "No" meant
safe. "Maybe" triggered a remote check against the full database.

**CDNs.** Akamai uses them to prevent caching one-hit wonders. Pages are only
cached if they hit the Bloom filter a second time.

## Properties

| Property        | Behavior                                         |
|-----------------|--------------------------------------------------|
| False positives | Possible—may say "yes" when answer is "no"       |
| False negatives | Impossible—never says "no" when answer is "yes"  |
| Deletion        | Not supported—removing a bit affects other items |
| Space usage     | Constant—grows with item count, not item size    |
