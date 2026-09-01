const command = process.argv[2] ?? "requested";

console.error(
  `Cannot run the root ${command} command: ReviewFlow applications have not ` +
    "been bootstrapped yet. See docs/roadmap.md for the task that introduces " +
    "the required application.",
);
process.exitCode = 1;
