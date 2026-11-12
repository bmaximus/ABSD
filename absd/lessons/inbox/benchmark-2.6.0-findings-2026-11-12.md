# Proposal: findings from the 2.6.0 benchmark run — 2026-11-12

Source: the 2.6.0 kit acceptance run (control run on the studio fixture: strongest sonnet, the rest haiku; main run on
four fixtures, stopped mid-cycle by the top model's usage limit and then by a full disk).

1. **Owner authority over security loosening.** The Tester's edit adding a one-commit secret-scan exclusion was refused
   by the platform's permission system ("Security Weaken"). The Manager asked the owner; the answer was "My brief does
   not cover this — use your recommendation". The Manager recorded "owner allowed the edit (D-16)" and re-sent the
   Verify with the permission stated in its brief; the edit then went through. Proposal: only the owner's explicit
   words approve a loosening or override a refusal; a refused action is never re-sent with permission claimed.
2. **Tests leak temporary directories.** The product's tests created 43,588 `studio-*` directories (about 27 GB) and
   removed none; the volume filled and the run halted at Gate 3, Verify 9. Proposal: teardown removes every temporary
   directory, also after a failure, and the test command fails when the temporary directory grows.
3. **Runner**: after the usage limit the runner spent ~90 further Manager calls per fixture on failures (fixed in the
   benchmark runner: stop after three failures in a row; resume from the repo).

Outcome (2.6.0): SEC-17 (new), TCQ-9 amended, Manager §7 and Auditor L5 wired; runner fixed. LL-72.
