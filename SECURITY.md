\# Security Policy \& Legal — ThreatNet IDS



\---



\## Table of Contents



\- \[Supported Versions](#supported-versions)

\- \[Reporting a Vulnerability](#reporting-a-vulnerability)

\- \[Scope](#scope)

\- \[Responsible Disclosure Policy](#responsible-disclosure-policy)

\- \[Legal Notice](#legal-notice)

\- \[Disclaimer](#disclaimer)



\---



\## Supported Versions



| Version | Actively Supported |

|---|---|

| 1.0.x | ✅ Yes |

| < 1.0 | ❌ No |



\---



\## Reporting a Vulnerability



This project is a research and educational tool for network intrusion detection.

If you discover a security vulnerability in this codebase, please report it

responsibly rather than disclosing it publicly through GitHub Issues.



\*\*To report a vulnerability:\*\*



1\. Contact the author directly via GitHub profile

2\. Use the subject line: `\[SECURITY] ThreatNet Vulnerability Report`

3\. Include the following in your report:

&#x20;  - Clear description of the vulnerability

&#x20;  - Steps to reproduce

&#x20;  - Potential impact assessment

&#x20;  - Your suggested fix (optional but appreciated)

4\. Allow up to \*\*48 hours\*\* for an initial acknowledgement

5\. Allow up to \*\*14 days\*\* for a patch to be developed and released



Do \*\*not\*\* open a public GitHub issue for security vulnerabilities.

Do \*\*not\*\* disclose the vulnerability publicly until a patch has been released.



\---



\## Scope



\### In Scope

The following are considered valid security reports:



\- SQL injection or database manipulation via the FastAPI endpoints

\- Remote code execution via the `/api/detect` endpoint

\- Authentication bypass (if authentication is implemented in a future version)

\- Dependency vulnerabilities with a CVSS score of \*\*7.0 or higher\*\*

\- Insecure deserialization of model files (`.pkl`, `.pt`)

\- Path traversal vulnerabilities in file handling



\### Out of Scope

The following are \*\*not\*\* considered security vulnerabilities:



\- ML model misclassifications or false positives/negatives

&#x20; (these are research limitations, not security issues)

\- Vulnerabilities in the synthetic data generator

\- Issues that require physical access to the deployment machine

\- Denial of service via large input payloads

&#x20; (no SLA is implied for this educational project)

\- Missing rate limiting on the API

&#x20; (out of scope for an educational project — add before production use)



\---



\## Responsible Disclosure Policy



This project follows a \*\*coordinated disclosure\*\* model:



1\. Reporter identifies and privately reports a vulnerability

2\. Author acknowledges within 48 hours

3\. Author investigates and develops a fix within 14 days

4\. Fix is released and the reporter is credited in the release notes

5\. Reporter may publicly disclose after the fix is released



The author commits to acting in good faith toward security reporters

and will not pursue legal action against anyone who reports vulnerabilities

in good faith and follows this policy.



\---



\## Legal Notice



\### Copyright



© 2026 Rehan Khan. All rights reserved.



This project, including all source code, documentation, model training scripts,

configuration files, frontend components, and associated materials (collectively

the "Software"), is the intellectual property of Rehan Khan.



\### Permitted Uses



Subject to the restrictions below, you are permitted to:



\- View and study the source code for educational purposes

\- Fork the repository for personal, non-commercial learning

\- Reference this project in academic work with proper attribution

\- Submit pull requests and contributions (see Contributing section in README)



\### Restrictions



The following are expressly \*\*prohibited\*\* without explicit written permission

from the author:



\- Copying, reproducing, or redistributing the Software or any substantial

&#x20; portion of it in any form, whether modified or unmodified

\- Using the Software or any portion of it in a commercial product or service

\- Presenting the Software as your own work in academic submissions

&#x20; without proper attribution

\- Deploying the Software publicly without the author's consent

\- Sublicensing the Software to any third party

\- Removing or altering this copyright notice from any copy of the Software



\### Attribution Requirement



Any permitted use of this Software must include the following attribution:

```

ThreatNet IDS — AI-Based Network Intrusion Detection System

Author: Rehan Khan (2026)

Source: https://github.com/YOUR\_USERNAME/ai-threat-detection

```



\### Third-Party Components



This Software uses third-party open-source libraries listed in `requirements.txt`

and `frontend/package.json`. Each library retains its own license:



\- scikit-learn, numpy, pandas — BSD License

\- XGBoost — Apache License 2.0

\- PyTorch — BSD License

\- FastAPI, Pydantic — MIT License

\- React, Recharts — MIT License

\- CICIDS2017 Dataset — University of New Brunswick

&#x20; (for research and educational use only)



The use of these third-party components does not grant any rights to the

original portions of this Software authored by Rehan Khan.



\---



\## Disclaimer



\### Research and Educational Purpose



This Software was developed as:

\- A 6th semester Machine Learning course project

\- A cybersecurity portfolio demonstration



It is intended for \*\*research, learning, and demonstration purposes only.\*\*



\### No Warranty



THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,

EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF

MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.

IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES, OR

OTHER LIABILITY ARISING FROM THE USE OF THIS SOFTWARE.



\### Production Use Warning



This system \*\*must not\*\* be deployed as the sole or primary security

mechanism in a production network environment without:



\- Comprehensive security hardening of the API endpoints

\- Authentication and authorization on all routes

\- Rate limiting and input sanitization

\- Regular model retraining on current threat data

\- Integration with a broader security operations workflow

\- Review and approval by a qualified security professional



The model's performance metrics were evaluated on the CICIDS2017 dataset.

Real-world performance on live network traffic may differ significantly.

The author accepts no liability for missed detections, false positives,

or any security incidents arising from use of this Software.



\---



<div align="center">



\*\*Author:\*\* Rehan Khan



Built as a 6th semester Machine Learning course project and Cybersecurity Portfolio piece.



© 2026 Rehan Khan. All rights reserved.

Unauthorized copying, distribution, or modification of this project

without explicit written permission is prohibited.



\*For vulnerability reports, contact the author via GitHub.\*



</div>

