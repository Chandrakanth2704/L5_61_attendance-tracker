# Lab 5: Static Code Analysis — Reflection

## 1. Purpose of Static Code Analysis

Static code analysis examines source code without executing it to identify potential bugs, security vulnerabilities, and coding-style violations. In this lab, I used Pylint, Bandit, and Flake8 to improve the quality, security, and maintainability of the Student Attendance Tracker.

## 2. Issues Identified and Fixed

The initial Pylint score was 4.55/10. The analysis identified problems including missing documentation, inconsistent naming, unused imports, a mutable default argument, and code-quality issues. Bandit reported insecure patterns involving disabled SSL verification, missing request timeouts, and shell execution. I updated the code to address these problems, added input validation, handled empty attendance records, and improved CSV export and resource handling.

## 3. Comparison of the Analysis Tools

Pylint helped identify code-quality and maintainability issues. Bandit highlighted potentially insecure coding patterns, while Flake8 identified style and formatting violations. Using all three tools provided complementary checks rather than relying on a single analyzer.

## 4. Results and Lessons Learned

After the changes, Pylint reported a score of 10.00/10, Bandit reported no issues, and Flake8 produced an empty report. Running the program again also confirmed that the demonstration completed successfully. I learned that static analysis is useful for finding problems early, but the results should also be reviewed alongside program behavior and the requirements of the application.
