# conditional-alpha

- **书里位置**: v5.7, Chapter 5 alpha discussion and mathematical appendix.
- **演示什么**: Conditional alpha as an information-measurable random variable; probability space, conditional expectation, L2 projection, residual orthogonality, and error under nested information.
- **迁移改了什么**: New self-contained teaching notebook. All four outcomes and their probabilities are specified explicitly. No textbook pages or market observations are included. QuantBook is initialized in QC; local Python reports itself distinctly.
- **跑通了吗**: Local default run passed on Python 3.12.7; unequal probabilities and 100 random parameter cases passed. QC cloud verification is recorded in README.md.
- **我学到什么**: The residual averages to zero within each observed group, but is not zero at each outcome. Changing the benchmark changes alpha, not the conditional forecast or residual. Full-outcome information is an unavailable oracle, not a deployable trading signal.

Prototype 0.1, 2026-09-22. `main.py` places no orders and exists only to package the research notebook through QC's backtest-sharing workflow.
