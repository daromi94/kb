# Flyweight

A structural pattern that reduces memory footprint when an application
needs a large number of similar objects. Instead of each object owning
all its data, the pattern factors out shared, immutable state into a
single reusable instance — the flyweight — and lets callers supply
context-dependent state at operation time.

This splits object state into two categories:

**Intrinsic state** — immutable data identical across many contexts.
Stored once inside the flyweight and shared freely.

**Extrinsic state** — data that varies per usage site. Never stored in
the flyweight; passed in by the caller.

## Structure

A FlyweightFactory acts as the sole entry point. It maintains a pool
keyed by intrinsic state, returning existing instances or creating new
ones on demand. Clients never instantiate flyweights directly.

```text
class Flyweight:
    constructor(sharedState):
        this.sharedState = sharedState # intrinsic, immutable

    operation(extrinsicState):
        doWork(this.sharedState, extrinsicState)

class FlyweightFactory:
    pool = {}

    get(key, sharedState):
        if key not in pool:
            pool[key] = new Flyweight(sharedState)
        return pool[key]
```

## Example — forest renderer

A game world with 2 million trees. Each species has identical mesh
data, bark texture, and leaf shader (intrinsic). Only position, scale,
and sway angle differ per tree (extrinsic).

```text
class TreeType:
    # intrinsic — shared across all trees of this species
    constructor(name, meshData, barkTexture, leafShader):
        this.name = name
        this.meshData = meshData
        this.barkTexture = barkTexture
        this.leafShader = leafShader

    # extrinsic — passed in per tree
    render(x, y, z, scale, swayAngle):
        transform = buildMatrix(x, y, z, scale, swayAngle)
        drawMesh(this.meshData, this.barkTexture, this.leafShader, transform)

class TreeFactory:
    cache = {}

    get(species):
        if species not in cache:
            config = loadSpeciesConfig(species)
            cache[species] = new TreeType(species, config.mesh, config.bark, config.leafShader)
        return cache[species]

class Forest:
    trees = [] # list of {flyweight, x, y, z, scale, sway}

    plant(species, x, y, z, scale):
        fw = TreeFactory.get(species)
        trees.append({flyweight: fw, x: x, y: y, z: z, scale: scale, sway: 0})

    renderAll():
        for t in trees:
            t.flyweight.render(t.x, t.y, t.z, t.scale, t.sway)
```

Two million trees, but roughly 15 TreeType objects in memory —
one per species. Mesh and texture data (often megabytes each) loads
exactly once.

## Design guidelines

**Get the intrinsic/extrinsic split right.** Intrinsic state is data
that would be identical if two instances were placed in completely
different contexts. If a value depends on *where*, *when*, or *who* is
using the object, it's extrinsic. Too much intrinsic state creates too
many unique flyweights (defeating the purpose); too much extrinsic
state burdens every call site.

**Intrinsic state must be immutable.** The moment shared state becomes
mutable, every consumer is coupled to every other consumer's mutations.
Enforce at the language level — `final` fields, frozen objects, `const`
references.

**Route all creation through the factory.** The factory is the single
source of truth for identity and deduplication. Direct instantiation
bypasses the pool and defeats sharing. Make the flyweight constructor
private or package-scoped.

**Choose key schemes carefully.** The factory key must uniquely and
completely identify the intrinsic state. Too coarse merges objects that
shouldn't be shared; too fine creates unnecessary duplicates.

**Consider struct-of-arrays layout.** At extreme counts (millions),
storing extrinsic state in parallel arrays rather than individual
wrapper objects further reduces overhead and improves cache locality
during batch operations.

**Lazy vs. eager population.** Lazy creation is the default. If the
full set is known at startup and initialization cost is high, eager
population avoids latency spikes at runtime.

**Profile before applying.** If total object count is in the hundreds
or per-object footprint is trivial, the indirection cost outweighs the
savings.

## Trade-offs

| Benefit                           | Cost                                  |
|-----------------------------------|---------------------------------------|
| Orders-of-magnitude RAM drop      | Extrinsic state scatters across sites |
| Reduced GC pressure               | Thread-safe factory required          |
| Shared flyweights stay hot        | CPU cache thrash if data is scattered |
| Single-point shared updates       | Debugging opacity (shared identity)   |
| Composes with Composite, Strategy | Over-engineering risk if no pressure  |

## Common applications

**Text rendering.** Glyph objects, character styles, font metrics
shared across millions of characters.

**Game engines.** Terrain tiles, particle systems, bullet pools,
tree/foliage instances, sprite atlases.

**GUI frameworks.** Shared border styles, icon resources, color
palettes, theme tokens.

**Connection management.** Shared protocol configs, TLS profiles
across thousands of connections.

**Language runtimes.** String interning (`String.intern()` in Java,
Python's small integer cache).

**3D scene graphs.** Shared geometry, materials, shaders with
per-instance transforms via instance buffers.

---

Return to [Patterns](_index.md)
