# Proposal: findings from the 2.7.0 benchmark run — 2026-11-18

Source: the 2.7.0 kit acceptance run (fixtures studio and shelf; strongest opus, balanced sonnet, fast haiku). The run
ended at about 10 hours when the machine restarted; neither fixture finished its Foundation cycle.

1. **The architecture review did not converge.** Studio failed Gate 2R five rounds in a row (AR-1 to AR-23) and the
   Manager parked the cycle (Mode P). Every round resolved its findings; the new findings sat in text the previous
   fix had added. A crash-safe restore grew a journal, then journal recovery, then recovery of an unreadable journal;
   a scheduled-backup fix added a retry rule with its own fault; the last round failed on an edit that split a
   numbered list. The 2.4.0 run failed the same gate once. Shelf also went many rounds and was sent back to the
   analysis and the design. The fixes added mechanism instead of narrowing scope, nobody tracked where new findings
   came from, and the escalation options did not offer to simplify the requirement driving the mechanism.
   Proposal: the Architect answers an AR with the smallest change and names any mechanism it adds; the Auditor tags
   each new AR with its origin; when new Critical or Major findings come mostly from the previous fix, the Manager
   escalates at once with a simplify option instead of another delta.
2. **Two known defects passed every gate and halted the Builder.** On shelf the test plan recorded that the analysis
   (keep 5 backups, never the one just taken) and the architecture's algorithm (keep 5 and always the one just taken)
   disagree when the clock moved back (5 vs 6 kept). The Tester marked it non-blocking and bound only the order where
   they agree; Gate T passed. The architecture also said a device fact "not VERIFIED by WP-8 is a Builder halt",
   i.e. it deferred verifying a world fact to the build; Gate 2R passed it. The Builder halted at WP-1 with both.
   Proposal: a disagreement between two specification sources on any reachable input is blocking; Gate 2R replays
   worked-number acceptance criteria through the specified algorithms; a blueprint never defers a fact's
   verification to a work package.
3. **Agents' own scripts leaked temporary directories.** One-off checks by the agents (probes, fact checks) created
   more than a thousand directories in the system temporary directory (574 MB in about 6 hours) and removed none.
   TCQ-9 covers product tests only. Proposal: every script an agent runs keeps its temporary files in one directory
   per invocation and removes it before replying, also on failure; the reply says so.

Outcome (2.7.1): ARCH-26 (new), ORACLE-7 amended, PIPE-9 (new); Architect, Auditor, Tester and Manager manuals and the
invocation brief wired. LL-75.
