# Static Code Analysis — Issue Log

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Disabled SSL certificate verification | Security — High | Original ERP sync function | `verify=False` disabled server certificate verification, making the connection vulnerable to interception. | Removed disabled verification and used the default secure TLS settings. |
| Shell command execution | Security — High | Original report backup function | Using `shell=True` with a command containing a wildcard could introduce command-injection risks. | Replaced shell-based archiving with Python's `tarfile` module. |
| Missing HTTP request timeout | Security — Medium | Original ERP sync function | An ERP request without a timeout could wait indefinitely. | Added a 10-second request timeout. |
| Outdated TLS protocol configuration | Security — Medium | Original TLS helper function | Explicitly selecting TLS 1.0 uses an outdated protocol. | Used `ssl.create_default_context()` to apply platform-default secure TLS settings. |
| Mutable default argument | Bug / Quality | Original `markAttendance()` function | A mutable dictionary default can be shared between calls. | Changed the default to `None` and initialized the register inside the function. |
| Empty attendance records | Bug / Quality | Original attendance percentage function | Calculating a percentage with zero records could cause division by zero. | Returned `0` when no attendance records exist. |
| Unused imports | Code Quality / Style | Original import section | Unused imports made the code less clean and maintainable. | Removed unused imports identified by the analysis tools. |
| Inconsistent function naming | Code Style | Original function definitions and call sites | CamelCase names did not follow the preferred Python `snake_case` convention. | Renamed functions and updated their call sites. |
| Missing documentation | Code Quality | Original module and function definitions | Missing docstrings made the code harder to understand and maintain. | Added a module docstring and function docstrings. |
| Formatting violations | Code Style | Original lines reported by Flake8 | Long lines and incorrect blank-line spacing reduced readability and violated style conventions. | Reformatted the code and corrected spacing. |

## Verification Results

- **Pylint:** 10.00/10, improved from 4.55/10.
- **Bandit:** No issues identified.
- **Flake8:** No violations reported.
