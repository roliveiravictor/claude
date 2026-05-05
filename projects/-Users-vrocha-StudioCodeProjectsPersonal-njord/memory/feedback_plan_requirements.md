---
name: Plans must include tests and documentation
description: Every implementation plan must have a Tests section and a Documentation section. User explicitly requires this.
type: feedback
originSessionId: e9e83698-0227-40ef-a991-af59a11ebc9a
---
Every plan must include:
- A **Tests** section listing what new unit/integration tests to write, with test names and what they assert
- A **Documentation** section specifying which `context/` files to update and what to add

**Why:** User corrected an omission and stated "every plan must update doc and tests." CLAUDE.md also says to keep `context/` docs updated when modifying code.

**How to apply:** Before calling ExitPlanMode, verify the plan has both sections. The Tests section should name the test file path, list individual test cases with setup and assertions. The Documentation section should name the specific `context/` file(s) and describe the content to add.
