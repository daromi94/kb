# Principles

Foundational design principles for software architecture.

## Notes

- [Abstraction](abstraction.md) - Hiding implementation to manage complexity
- [Uniform access](uniform-access.md) - Hide whether a value is stored or computed
- [Indirection](indirection.md) - Adding layers between requester and provider
- [Polymorphism](polymorphism.md) - Many shapes through common interfaces
- [Inheritance design](inheritance-design.md) - Design for extension or prohibit it; prefer composition
- [Law of Demeter](law-of-demeter.md) - Only talk to your immediate friends
- [Tell, don't ask](tell-dont-ask.md) - Command objects, don't query their state
- [Command-query separation](command-query-separation.md) - Methods should change state or return data, not both
- [Information expert](information-expert.md) - Assign responsibility to the class that holds the data
- [Getter eradicator](getter-eradicator.md) - Diagnostic exercise: challenge every getter
- [Anemic domain model](anemic-domain-model.md) - Anti-pattern of behavior-free domain objects

---

Return to [Practices](../_index.md)
