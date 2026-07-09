# Verification missions

A mission is one mathematical claim (or a small bounded set) put under the
council. Keep each mission small enough that the formalizer can attempt the
decisive step in Lean.

Start by validating the machine, not by attacking open problems:

1. **Known-theorem check** — feed a claim that is a known theorem. The prior-art
   auditor should return `known` with a citation. If it calls it novel, the
   machine is broken.
2. **Injected-error check** — feed an argument with one deliberately false step.
   The skeptic must return `refuted` with the exact `breaks_at`. If it approves,
   the machine is broken.
3. **Small true lemma** — feed a genuine, provable lemma. The formalizer should
   produce a Lean file that builds, and only then does it become `proven`.

Only after the machine passes 1–3 should you point it at sub-problems of a real
open question — and even then, the honest output is "here is a verified lemma" or
"this step does not formalize", never "here is a proof of the big conjecture".

## Registry

| Mission | Claim (short) | Kind | Latest status |
|---|---|---|---|
| _M-000_ | _example: sum of two even integers is even_ | true-lemma | _not run_ |

Each run lands in `.adversal/runs/<run-id>/` with its brief, worker
assessments, Lean artifacts, and `verdict.json`.
