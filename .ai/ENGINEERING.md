# Engineering Instructions:

1. Apply SOLID Principles Pragmatically:
   1.1. Single Responsibility: Components store one type of data, systems handle one type of behavior. Each component represents a single aspect of an entity. Each system processes a single concern.
   1.2. Open/Closed: Add new components and systems without modifying existing ones. New behavior comes from new systems operating on new or existing components. Extend functionality through composition, not modification.
   1.3. Liskov Substitution: Systems should work correctly with any entity containing their required components. If a system queries for specific components, it must handle all entities with those components uniformly.
   1.4. Interface Segregation: Keep components minimal and focused. Systems should query only for the components they need. Don't bundle unrelated data into mega-components.
   1.5. Dependency Inversion: Systems depend on component types, not specific entity implementations. Systems shouldn't know about entity archetypes or make assumptions about what other components an entity might have.
2. Write Less Code: Keep implementations minimal. Choose the 20-line solution over the 100-line one. Delete code that might be useful "someday." Value clarity over cleverness.
3. Structure Code in Logical Blocks: Avoid extracting functions unless they're used multiple times. Write sequential, readable blocks with clear comments marking each section's purpose. Let the code tell a story from top to bottom.
4. Use Early Returns Liberally: Exit functions as soon as possible. Check preconditions first, handle edge cases early, keep the main logic at the lowest nesting level.
5. Comment Every Logical Section: Start each code block with a comment explaining its purpose. Focus on "why" not "what"—the code shows what, comments explain intent.
6. Name Everything Explicitly: Use object parameters with named properties instead of positional arguments. Make function calls self-documenting through parameter names. Choose verbose clarity over brief ambiguity.
7. Maintain Type Safety Throughout: Never use any. Define types for everything. Let TypeScript catch errors at compile time, not runtime. Trust the compiler to be your first line of defense.
8. Fail Fast and Loud: Don't handle errors—let them crash immediately. The system must work correctly or not at all. Use assertions liberally during development.
9. Embrace External Solutions: Use battle-tested libraries and industry-standard approaches for solved problems. Don't reinvent common algorithms, data structures, or utilities.

# Practical Tools:

1. The project is big – when you struggle to find something, ask the user, they'll be happy to point you directions.
2. Prefer to read full files when inspecting code.