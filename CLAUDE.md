Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

Tradeoff: These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
- Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.
- Max 5 functions per page.
- No more than 30 lines per function.

If you can use a library like pydantic or ast or others known and reliable libraries, ask the user first and use them.

Function length: aim for 25 lines. This is a guideline, not a hard limit —
a function may go slightly over when it does one thing cleanly. The real
principle behind the number: a function should do ONE thing, fit on one
screen (readable without scrolling), and stay at a single level of
abstraction. Respect that and length usually falls under 25-30 on its own.
The number is just the warning light for the principle — if you're far over,
the function is doing too much: split it by responsibility, never split it
just to hit the number.

## 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

If something that you want to write is deprecated (see console), rethink and correct it.

## 4. Goal-Driven Execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Project Structure & Tooling (Python)

Organize by responsibility. Keep it flat until size demands otherwise.

- Group related modules into packages ONLY when a folder grows beyond
  a few files or a clear responsibility emerges. Don't pre-split small code.
- Each package gets an `__init__.py`. Keep it minimal — an empty file is fine.
  Expose only the package's public API there, not every symbol.
- Imports go at the top of each file. Repeating an import across files is
  normal Python, not duplication — do not "fix" it.
- Remove unused imports (see rule 3). Never add imports inside functions
  unless avoiding a genuine circular dependency.
- Use `uv` for dependency management and virtual environments.
- Create a sub-package when a clear responsibility emerges, never to hit a
  number (no fixed "max N imports/files per level"): grouping by count
  produces meaningless folders and hides dependencies.
- No import cycles between packages. When two packages genuinely depend on
  each other, move the misplaced module rather than working around it.

The test: structure should reflect responsibility, not impress. If a
senior would say "this is split up for no reason", flatten it.

## 6. Project-Specific — ats-simulator

- **Stack**: Python 3.11+, `uv` per dipendenze/venv, build backend `hatchling`.
- **Librerie approvate**: `pydantic` (modelli dati/validazione), `pdfplumber` (estrazione testo/coordinate PDF), `python-docx` (estrazione testo DOCX). Nessuna altra libreria esterna senza chiedere prima.
- **Nessuna integrazione a servizi esterni runtime**: niente chiamate a OpenCATS, RChilli, Sovren o altre API di parsing nel prodotto. OpenCATS è stato studiato solo come ispirazione strutturale (organizzazione a moduli per dominio di business) e poi rimosso dal filesystem — non è una dipendenza. Le capacità avanzate (parsing layout-aware multi-colonna, normalizzazione skill) sono costruite in proprio, informate da ricerca pubblica su come funzionano i motori enterprise (vedi `PLAN.md`), usando dataset pubblici (ESCO/O*NET) per la tassonomia skill.
- **Organizzazione**: package-by-feature (`parsing/`, `scoring/`), non per layer tecnico. Dentro ogni pacchetto: dati come modelli `pydantic` (es. `ParsedResume`), logica come funzioni pure (max 30 righe), classi solo dove serve incapsulare stato reale — niente gerarchie di ereditarietà o design pattern enterprise-Java non necessari qui.
- **Destinazione**: questa repo è una libreria Python installabile standalone (non uno script), pensata per essere aggiunta come dipendenza git (`uv add git+...`) da un futuro repo che orchestrerà l'intera pipeline del prodotto. L'API pubblica esposta in `src/ats_simulator/__init__.py` è il contratto verso quel repo — va mantenuta minima e stabile.
- **Interfaccia attuale**: libreria importabile + CLI minima per test manuali in locale. Nessun server/API HTTP in questa fase.
- Riferimento completo alle decisioni di architettura e alla ricerca di mercato/tecnica: `PLAN.md` in questa stessa repo.
