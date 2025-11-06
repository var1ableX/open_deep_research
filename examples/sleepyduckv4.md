# SleepyDuck Malware in Open VSX: Dissection of a Sophisticated Supply Chain Attack

## Executive Summary

A highly sophisticated supply chain attack was uncovered in November 2025 with the discovery of SleepyDuck, a remote access trojan (RAT) embedded in a malicious Solidity extension on the Open VSX marketplace. Targeting developers using popular code editors such as Cursor and Windsurf, attackers initially published a benign version of the extension before deploying a malicious update that leveraged anti-analysis, sandbox evasion, delayed payload activation, and innovative blockchain-based command and control (C2) mechanisms. This incident rapidly exposed thousands of developer systems and highlighted critical weaknesses in extension marketplace security and the broader software development supply chain.

**Key Findings:**

- **Vector / Entry Point** — Malicious payload embedded in an updated version of a Solidity helper extension (juan-bianco.solidity-vlang) on Open VSX, exploited by compromise of extension updating and trust in high-download packages.
- **Impact** — Direct compromise of at least 14,000 developer systems, with over 53,000 downloads before removal; exposure includes remote code execution, credential theft, and secondary software supply chain risk.
- **Actor / Attribution** — No confirmed public attribution; actor demonstrates advanced anti-analysis skills and operational security, consistent with financially motivated or advanced persistent threat (APT) profiles.
- **Technique / Innovation** — Utilization of blockchain-based C2 via Ethereum smart contract for resilient fallback, delayed activation, and sandbox detection to evade traditional detection and takedown.
- **Relevance** — Marks a profound escalation in supply chain threats targeting developer ecosystems, using persistent and decentralized control channels and eroding trust in major extension marketplaces.

## Attack Overview

SleepyDuck was introduced through a seemingly legitimate Open VSX extension, masquerading as a Solidity language helper and capitalizing on the trusted reputation and high download counts of its target. The initial extension (version 0.0.7, published October 31, 2025) was benign, allowing the attacker to amass thousands of installations and credibility in the registry[1][2]. A subsequent update (version 0.0.8, released November 1) weaponized the extension with malicious RAT functionality, delivered as an automatic update to unsuspecting developers[1][3]. SleepyDuck specifically targeted Windows environments and activated only during specific developer actions—such as opening a code editor window, selecting Solidity files, or running build commands—to further avoid automated scanning and initial sandbox review[1][2].

The attack coincided with a surge of similar fraudulent Solidity extensions on both Open VSX and Visual Studio Code marketplaces since July 2025, part of a broader trend of supply chain threats exploiting developer tool ecosystems[2][4]. As a result, large-scale developer compromise risked downstream contamination of organizational codebases and broader project supply chains.

## Attacker Profile

No threat actor or group has been definitively linked to the SleepyDuck campaign as of November 2025. Security analysis and threat intelligence feeds consistently describe the operator as skilled, persistent, and well-resourced, leveraging a unique blend of technical innovations and operational security:

- **Origin & Activity:** No public attribution to a criminal group, APT, or specific individual. The malware’s sophistication, including blockchain-based C2 and advanced evasion, suggests a highly technical operator potentially motivated by financial gain or access to sensitive developer environments[1][2].
- **Historical Context:** The campaign is part of a continued series of malicious “Solidity” extensions since July 2025, with at least 20 documented cases; however, evidence linking SleepyDuck to specific actors from past extension attacks (e.g., those by “developmentinc”) remains unproven[2][4].
- **Signature TTPs:** The actor exhibits a careful approach, abusing extension update workflows, employing delayed activation and sandbox detection, and using blockchain for decentralized command control.

## Tools and Payload Characteristics

### SleepyDuck Remote Access Trojan

- **Nature:** JavaScript-based RAT embedded in the extension file tree, invoked through typical developer actions.
- **Persistence:** Activates on IDE startup, file selection (.sol), or compilation events, creating a lock file for single execution per session[1][2].
- **Evasion:** Employs anti-analysis behaviors including:
  - Sandbox environment checks (machine/user info, MAC, timezone) to avoid execution in automated or researcher-controlled environments[1][2].
  - Delayed/conditional execution to defeat basic static and dynamic scans[1][2].
- **Command and Control:**  
  - Default: HTTP(s) POST polling against sleepyduck.xyz every 30 seconds for instructions, exfiltrating hostname, username, MAC address, and timezone[1][2][3].
  - Fallback: If primary C2 is unavailable, fetches new C2 configuration from an Ethereum smart contract (0xDAfb81732db454DA238e9cFC9A9Fe5fb8e34c465) using the fastest available public Ethereum RPC endpoint, providing resilient and covert external C2[1][2][3].
- **Update Mechanism:** The extension is updated via standard Open VSX channel, with the malicious code pushed only after critical install numbers are reached, imitating “trust-on-first-use” but weaponized post-factum.

## Attack Chain

### Step-by-Step Overview with MITRE ATT&CK Mapping

1. **Initial Access**
   - **Action:** The malicious extension is uploaded to Open VSX as a benign utility (“juan-bianco.solidity-vlang” v0.0.7).
   - **MITRE Tactic:** TA0001 Initial Access
   - **Technique:** T1195.002 Supplying Malicious IDE Extensions through Trusted Marketplace[5]
2. **Establishment and Update**
   - **Action:** Rapid accumulation of installs (>14,000 downloads). After earning trust and audience, extension is stealthily updated (v0.0.8) with embedded RAT.
   - **MITRE Tactic:** TA0003 Persistence / TA0005 Defense Evasion
   - **Techniques:** T1176.002 IDE Extension Persistence; T1546.011 Application Rootkit (IDE/plugin hijack)
3. **Execution**
   - **Action:** Triggered by developer opening the IDE, selecting .sol files, or compiling code, the extension initializes the malware, collects system info, and performs sandbox checks.
   - **MITRE Tactic:** TA0002 Execution / TA0006 Credential Access
   - **Techniques:** T1059.007 JavaScript Execution; sandbox detection to avoid analysis[1][2]
4. **Defense Evasion**
   - **Action:** SleepyDuck avoids early detection through delayed activation, sandbox/environmental triggers, and obfuscation.
   - **MITRE Tactic:** TA0005 Defense Evasion
   - **Techniques:** T1497.001 Virtualization/Sandbox Evasion; T1027 Obfuscated Files or Information
5. **Command and Control**
   - **Action:** Periodic (every 30 seconds) HTTPS connection to sleepyduck.xyz C2 for tasking—on failure, polls Ethereum blockchain smart contract for updated C2 configuration.
   - **MITRE Tactic:** TA0011 Command and Control
   - **Techniques:** T1071.001 Web Protocol; T1090.003 Multi-Stage Channels; T1102 Web Service
   - **Innovation:** Blockchain-based C2 fallback (Ethereum smart contract dead-drop), making takedowns ineffective[1][2][3].
6. **Collection**
   - **Action:** Gathers and sends host intelligence (hostname, username, MAC, timezone) to C2.
   - **MITRE Tactic:** TA0009 Collection
   - **Technique:** T1005 Data from Local System
7. **Impact**
   - **Action:** Operator-enabled remote access—potential for further credential harvesting, persistent foothold, lateral movement within developer and enterprise networks, and risk of propagation through continuous integration/continuous deployment (CI/CD) or software release pipeline contamination[1][2][4].

## Impact

### Direct Impact

- **Developer Workstations:** SleepyDuck granted attackers remote execution privileges, opening the possibility of source code theft, credential exfiltration, project manipulation, and lateral spread throughout organizational networks[2][3].
- **Credential Exposure:** System and developer account credentials, including possible cloud, NPM, GitHub, or cryptocurrency secrets, were at risk of exfiltration and further compromise[2][4].
- **Downstream Supply Chain:** Infection on development endpoints threatened to propagate malicious code or secrets into CI/CD systems and shipping software artifacts, raising the stakes for downstream consumers[2][4].

### Indirect Impact

- **Marketplace Integrity:** The incident damaged trust in Open VSX and similar extension ecosystems, highlighting the risk of extension propagation, update-based compromise, and supply chain insertion attacks[3][4].
- **Resilience Challenge:** SleepyDuck’s blockchain-based C2 neutralized classic network-based defenses and takedown strategies, demanding new defensive paradigms[2][3].
- **Active Threat Window:** Over 53,000 installations recorded during the attack window, including a period where the malicious version remained online despite platform warnings[1][2].
- **Broader Vulnerability:** Reinforces the challenge posed by extension auto-updates and the long tail of “trusted” but vulnerable or hijackable software supply chain components.

## Tactical Defense Recommendations

### Analytical Summary

The SleepyDuck incident demonstrates that adversaries can weaponize the entire extension update workflow, and that reliance on download counts or reputational cues is no defense against latent supply chain compromise. The use of decentralized, blockchain-based C2 that cannot be easily shut down further erodes confidence in traditional network defenses. This event highlights urgent requirements for real-time extension vetting, explicit publisher attestation, rigorous inventory and allowlisting, and enhanced monitoring of anomaly indicators in developer environments.

### Immediate Action Checklist

*(*Each item maps to NIST CSF v2 where relevant; PR = Protect, DE = Detect, ID = Identify, RS = Respond, RC = Recover*)*

- **Audit and Inventory Extensions** (ID.AM-01, PR.PS-02)
  - Enumerate all IDE/editor extensions deployed across developer workstations. Remove or disable any with unknown provenance or recent update anomalies—especially any matching “juan-bianco.solidity-vlang.”
- **Implement Allowlisting for Extensions** (PR.PS-02, PR.AC-01)
  - Restrict installation only to approved, security-reviewed extensions from trusted or internally verified sources. Disallow user-level arbitrary extension installation in sensitive environments.
- **Mandate Extension Update/Changelog Review** (PR.PS-03, PR.MA-01)
  - Require manual review of extension updates/changelogs before approving upgrades in controlled workspaces, especially for high-privilege or shared workstations.
- **Conduct Immediate Threat Hunt and Forensic Review** (DE.CM-07, DE.CM-08)
  - Search for SleepyDuck IOCs (extension name, sleepyduck.xyz, Ethereum contract 0xDAfb81732db454DA238e9cFC9A9Fe5fb8e34c465) within all managed networks and endpoints. Investigate any C2 callback or executed JavaScript modules through the editor process.
- **Rotate All Credentials and Secrets** (PR.AA-04, PR.AA-05, PR.AA-07)
  - Reset passwords, tokens, and API keys associated with any compromised environment; invalidate any long-lived tokens used within source code, CI/CD, or artifact registries.
- **Strengthen CI/CD Pipeline Security** (PR.DS-06, PR.AC-06, PR.MA-03)
  - Pin all dependencies to immutable commits; restrict third-party extensions/actions; enforce access reviews; monitor pipeline changes and audit logs for anomalous actions.
- **Deploy Network and Endpoint Monitoring** (DE.CM-02, DE.CM-03)
  - Leverage continuous anomaly-based detection incorporating threat intelligence and custom SleepyDuck IOCs. Monitor for suspicious network flows (periodic outbound polling, unexpected connections to Ethereum RPC endpoints, or the C2 domain).
- **Automate Extension/Marketplace Threat Intelligence Integration** (ID.RA-05, DE.CM-08)
  - Sync extension signature feeds and blocklists from threat vendors; subscribe to timely advisories covering new malicious extension campaigns and C2 infrastructure changes.
- **Educate Developers and End-Users** (PR.AT-01, PR.AT-02)
  - Enforce regular, targeted training on supply chain and extension-based attack threats; build and communicate an incident response plan for rapid notification and remediation if compromise is detected.
- **Engage Incident Response and Recovery Protocols** (RS.RE-01, RS.CO-02, RC.IM-01)
  - Prepare and test incident playbooks for rapid isolation, reimaging, credential revocation, and downstream notification following supply chain attack detection; inform impacted parties and regulators as necessary.

## Sources

[1] Secure Annex: SleepyDuck malware invades Cursor through Open VSX – https://secureannex.com/blog/sleepyduck-malware/  
[2] GBHackers: 'SleepyDuck' Malware in Open VSX Lets Attackers Remotely Control ... – https://gbhackers.com/sleepyduck-malware/  
[3] The Hacker News: Malicious VSX Extension "SleepyDuck" Uses Ethereum to Keep Its ... – https://thehackernews.com/2025/11/malicious-vsx-extension-sleepyduck-uses.html  
[4] BleepingComputer: Fake Solidity VSCode extension on Open VSX backdoors developers – https://www.bleepingcomputer.com/news/security/fake-solidity-vscode-extension-on-open-vsx-backdoors-developers/  
[5] MITRE ATT&CK: IDE Extensions, Sub-technique T1176.002 – https://attack.mitre.org/techniques/T1176/002/  
[6] Wiz Blog: Supply Chain Risk in VSCode Extension Marketplaces – https://www.wiz.io/blog/supply-chain-risk-in-vscode-extension-marketplaces