const command = process.argv[2] ?? "requested";

console.error(
  `Cannot run the root ${command} command: ReviewFlow has no corresponding ` +
    "artifact yet. See docs/roadmap.md for the task that introduces it.",
);
process.exitCode = 1;
