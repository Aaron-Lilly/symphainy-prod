# Stability & Gravity Report

**Artifact Type:** Architectural Stability & Gravity Report  
**Scope:** <one layer, service, or cross-cutting concern>  
**Epoch:** <date or iteration name>

---

## A. What Was Probed

- **Change introduced:**
- **Trigger:** (feature, refactor, config change, deploy, traffic, etc.)
- **Expected impact (in human terms):**

---

## B. Observed Behavior

- **What broke:**
- **Where symptoms appeared:** (browser / logs / startup / runtime / network)
- **Time to failure:** (immediate / delayed / under load)

---

## C. Stability Signals

Answer yes/no and describe:

- **Did unrelated components break?**
- **Did restarting "fix" it temporarily?**
- **Did the failure move when we changed order of startup?**
- **Did configuration changes have outsized effects?**

---

## D. Gravity Signals

Answer yes/no and describe:

- **Did logic migrate back into a specific service/module?**
- **Did agents need extra context to compensate?**
- **Did responsibilities blur across layers?**
- **Did fixes require touching many files?**

---

## E. Hypotheses (Do NOT Resolve)

- **Suspected unstable boundary:**
- **Suspected missing contract:**
- **Suspected premature abstraction:**

*No fixes here. Only hypotheses.*

---

## F. Classification

- [ ] Collapsing abstraction
- [ ] Leaky boundary
- [ ] Stable seam
- [ ] Unknown / needs more probes

---

## G. Recommendation

One of:

- **Probe again with variation**
- **Isolate behind temporary adapter**
- **Freeze and document**
- **Defer intentionally**
