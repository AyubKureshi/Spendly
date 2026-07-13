---
description: Run test-writer then test-runner for a Spendly feature
argument-hint: "Feature name e.g. login"
allowed-tools: Read, Write, Glob, Bash, Agent
---

You are a senior developer automating the test workflow for Spendly.

User input: $ARGUMENTS

## Step 1 — Validate input
If $ARGUMENTS is empty, ask the user to provide a feature name (e.g., "login", "registration").

## Step 2 — Run test-writer agent
Invoke the spendly-test-writer agent with the prompt:
"Write pytest tests for the $ARGUMENTS feature."
Wait for the agent to complete and capture its output.

## Step 3 — Run test-runner agent
Invoke the spendly-test-runner agent with the prompt:
"Run and analyze the tests for the $ARGUMENTS feature."
Wait for the agent to complete and capture its output.

## Step 4 — Show output
Print the output from the test-runner agent to the user.