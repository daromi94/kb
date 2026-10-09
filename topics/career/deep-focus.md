# Deep focus

Deep focus means working on one task without interruptions. It helps with work that takes time to understand, such as debugging, reading technical material, or comparing designs.

Suppose an engineer is investigating a slow request. After answering a message, they may need to reread the code and remember what they already checked. Repeated interruptions leave less time to investigate the problem.

## Choose one clear task

"Work on the service" is too broad. Choose something specific:

- Find where a request spends most of its time.
- Reproduce one bug.
- Compare two ways to move data to a new system.
- Read one section and explain how it works.

A clear task makes it easier to start and notice progress. For a slow request, the steps might be:

```text
Trace the request
        |
Measure the time spent at each step
        |
Find the slowest step
        |
Decide what to check next
```

Choose reading material that helps answer the current question. Open the relevant chapter or source file, and save unrelated articles for later.

## Make room for uninterrupted work

Before starting:

- Close unrelated tabs.
- Silence notifications that can wait.
- Open the files and notes needed for the task.
- Keep urgent alerts available if the job requires a quick response.

Where possible, check routine messages at set times and group small tasks together. This leaves longer periods for work that needs concentration.

A quiet workspace and a simple starting routine can make it easier to begin. During incident duty, shorter sessions or coverage from a teammate may be needed.

## Write down where to resume

Before stopping, write down:

- What was learned.
- What is still unclear.
- What to do next.

For example:

```text
Found:   requests wait for a database connection.
Unknown: why the connections stay busy.
Next:    measure how long each request keeps its connection.
```

The next session can begin with that measurement instead of repeating the investigation.
