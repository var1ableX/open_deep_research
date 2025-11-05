# SleepyDuck -A Modern Supply Chain Threat Emerges in the Developer Ecosystem

## Incident Overview and Significance

In late October 2025, the developer world witnessed an advanced supply chain attack that unfolded through the Open VSX marketplace—a widely utilized, community-driven extension registry for code editors such as Cursor and Windsurf. Attackers uploaded a seemingly benign Solidity IDE extension, titled "juan-bianco.solidity-vlang," which, after initial publication and trust-building downloads, surreptitiously delivered a malicious update (version 0.0.8) that activated the SleepyDuck malware. Unbeknownst to tens of thousands of developers, this extension weaponized their environments, enabling remote control, credential theft, and further compromise. The attack’s stealth mechanisms—delayed activation, obfuscated code, and blockchain-based failover for command communication—rendered it especially difficult to detect and dismantle.

This event is not merely an isolated breach but a demonstration of how supply chain compromise in open developer marketplaces can become a blueprint for rapidly replicable campaigns. As these platforms gain prominence in fast-paced, AI-driven coding workflows, the incident signals a warning to all organizations: trust can be undermined at the extension layer, turning innovation ecosystems into vectors for persistent and widespread compromise[1][2][3][4][6][13][8][15].

## Technical Investigation

### Attacker Background and Profile

While public sources have not conclusively attributed SleepyDuck to a named group, the campaign bears the hallmarks of a seasoned, technically adept threat actor. Notably, this operator has a track record of publishing malicious packages disguised as popular or trending development tools, frequently exploiting typosquatting and fake publisher personas. Activity patterns and fast follow-up with new malicious packages suggest high motivation and resourcefulness, but there is currently no known affiliation with a specific nation-state or recognized APT group[3][6][8].

### Toolset and Obfuscation Methods

SleepyDuck’s arsenal was embedded in a commonly used IDE extension, cunningly wrapped in JavaScript and activated via multiple editor events:

- **Multi-Event Payload Activation:** The malware executed not only on IDE startup but also whenever a new window opened, a Solidity file was accessed, or code was compiled. This broad activation surface ensured nearly continuous operation.
- **Sandbox and Anti-Analysis Features:** Prior to full activation, the payload collected system telemetry—hostnames, usernames, MAC addresses, time zones—and included logic to detect analysis or virtualized environments, suppressing its activities if such conditions were present.
- **Sophisticated Obfuscation:** The malicious code was layered with obfuscation to foil static and behavioral analysis tools, requiring detailed manual investigation to uncover its logic and behavior[1][2][3][4][6][13].

### Blockchain-Based Command and Control

SleepyDuck’s standout innovation is its use of a dual-channel command and control (C2) strategy:

- **Primary C2 Channel:** The malware initially reported to sleepyduck[.]xyz every 30 seconds, exfiltrating basic recon data and awaiting remote commands.
- **Blockchain C2 Failover:** If the primary domain was neutralized, SleepyDuck queried an Ethereum smart contract (0xDAfb81732db454DA238e9cFC9A9Fe5fb8e34c465), retrieving updated C2 endpoints, polling intervals, or even emergency instructions via the blockchain—making takedown substantially harder. Critical C2 updates and attacker instructions could thus persist immutably, resilient against domain seizures or cloud shutdowns[1][2][3][4][6][13][15].

![[Pasted image 20251104162713.png]]
![[Pasted image 20251104162737.png]]
### Damage and Exposure

The real and potential impacts of SleepyDuck are severe:

- **Direct Losses:** Confirmed theft of high-value crypto assets, complete compromise of developer workstations, and loss of credentials[1][2][3][4][6][8][13].
- **Software Integrity Risk:** Potential for injection of malicious code within proprietary repositories or open-source contributions, with downstream risk for all software consumers.
- **Supply Chain Blast Radius:** Any organization consuming code, containers, or CI/CD artifacts touched by compromised machines could become an unwitting victim—extending risk beyond initial targets[3][4][6][8][13].
- **Regulatory/Incident Response:** The use of blockchain for C2 complicates regulatory notification timelines and thorough post-incident investigations, as evidence is distributed, persistent, and hard to erase[13][16].
- **Erosion of Trust:** Trust in community-driven extension marketplaces is undermined, with typosquatted, bot-inflated, and SEO-gamed packages rising in search rankings over genuine extensions[8].

### Unanswered Questions and Gaps

- **Attacker Attribution:** No public evidence attributes SleepyDuck to a named actor or group; further intelligence gathering is ongoing.
- **Post-Compromise Depth:** Details of specific lateral movement, payload variants, and extent of internal ecosystem spread remain largely within proprietary threat reports.
- **Downstream Impact:** The full extent of downstream environments and customer projects potentially compromised via tainted developer systems is not precisely known.

## Tactical Response Plan

### Analytical Summary

The SleepyDuck incident exposes critical weaknesses at the intersection of software supply chain trust, open extension marketplaces, and remote access malware. SleepyDuck’s success stemmed from manipulating developer trust, exploiting a lack of marketplace vetting, leveraging anti-analysis and obfuscation, and deploying a robust blockchain-based C2 failover architecture. These elements together transformed a simple code editor add-on into a persistent, resilient compromise platform.

## Defense and Mitigation Checklist

|Key|Description|
|---|---|
|Inventory and Restrict Extension Usage|Identify and document all IDE extensions in use; ban unapproved or unverified extensions using allow-lists.  <br>Disable automatic or silent extension updates in both managed and individual environments.  <br>[NIST CSF: ID.AM-01, PR.PT-03][1][4][8][13]|
|Implement Publisher Verification and Monitoring|Only trust and deploy extensions from verified publishers. Cross-check publishers’ identities, scrutinize for typosquatting and excessive download count manipulation.  <br>[NIST CSF: PR.AC-01, PR.DS-01][8][13]|
|Continuous Monitoring and Threat Detection|Deploy endpoint monitoring that can detect “known bad” C2 activity (e.g., sleepyduck.xyz), unusual access to Ethereum RPC endpoints, or unknown process spawning from IDEs.  <br>Monitor for installation or activation of remote access tools post-extension compromise (such as ScreenConnect, Quasar RAT, or PowerShell scripts).  <br>[NIST CSF: DE.CM-01, DE.CM-08][8][13]|
|Credential and Secret Rotation|Immediately rotate all credentials, session keys, and API tokens potentially exposed. Enforce hardware-backed wallets/storage and multi-factor authentication wherever possible.  <br>[NIST CSF: PR.AC-04, PR.DS-05][8][13][16]|
|Audit and Isolate High-Risk Development Systems|Segregate compromised developer environments, especially those involved in sensitive or production resource access. Sweep these environments for additional payloads, backdoors, or lateral movement.  <br>[NIST CSF: PR.IP-09, DE.DP-01][8][13]|
|Supply Chain Governance|Maintain a software bill of materials (SBOM) for all internally developed and consumed software.  <br>Treat IDE extensions, plugins, and external development dependencies as in-scope for vulnerability and risk management processes.  <br>[NIST CSF: ID.RA-03, GV.SC-01][10][16][19]|
|Advance Upstream Pressure|Work with upstream marketplace maintainers to improve extension vetting, publisher reputation mechanisms, and require cross-platform publisher identity verification to minimize typosquatting and malicious search manipulation.  <br>[NIST CSF: GV.SC-02][2][4][8]|
|Immediate Extension Audit|Manually inspect and uninstall any suspicious, infrequently used, or publisher-unknown extensions. Pay special attention to subtle character changes in extension names or publishers.  <br>[NIST CSF: PR.PT-04][4][8][13]|
|System Deep-Cleanse|Run comprehensive antimalware and security scans; check for unauthorized remote access tools; delete and quarantine harmful executables or scripts found.  <br>[NIST CSF: DE.CM-07][8]|
|Credential Hygiene|Reset all passwords, clear cached credentials, and securely rotate wallets or sensitive keys.  <br>[NIST CSF: PR.AC-03, PR.DS-06][8][13]|
|Safe Extension Practices|Never install extensions purely based on download counts or search rankings. Validate all publisher GitHub links, review extension code if possible, and consult verified, community-endorsed extension lists.  <br>[NIST CSF: PR.IP-04][8][13]|
|Monitor for IoCs|Proactively block outgoing connections to documented C2 domains (e.g., sleepyduck.xyz) and monitor for outbound Ethereum smart contract calls tied to known attacks.  <br>[NIST CSF: DE.CM-03][1][4][8][13]|
|Key Indicators of Compromise (IoCs)|- Malicious extension: `juan-bianco.solidity-vlang`<br>- Typosquatted publisher: `juanbIanco` (with uppercase 'I')<br>- C2 domain: sleepyduck[.]xyz<br>- Ethereum contract: 0xDAfb81732db454DA238e9cFC9A9Fe5fb8e34c465<br>- Secondary malware artifacts: Quasar RAT, ScreenConnect, PureLogs payloads|

## Sources

1. [SleepyDuck malware invades Cursor through Open VSX](https://secureannex.com/blog/sleepyduck-malware/)
2. [Fake Solidity VSCode extension on Open VSX backdoors developers](https://www.bleepingcomputer.com/news/security/fake-solidity-vscode-extension-on-open-vsx-backdoors-developers/)
3. ['SleepyDuck' Malware in Open VSX Lets Attackers Remotely Control ...](https://gbhackers.com/sleepyduck-malware/)
4. [Malicious VSX Extension “SleepyDuck” Leverages Ethereum for ...](https://malware.news/t/malicious-vsx-extension-sleepyduck-leverages-ethereum-for-command-and-control/101011)
5. [Cyber News Live on X](https://x.com/cybernewslive/status/1985493660654346677)
6. [SleepyDuck Malware Redefines C2 Resilience with Ethereum ...](https://malware.news/t/sleepyduck-malware-redefines-c2-resilience-with-ethereum-blockchain/100988)
7. [International : l'actu du Jour - No Hack Me](https://www.nohackme.com/news-action-international.html)
8. [Fake Solidity VSCode Extension on Open VSX Used ...](https://www.rescana.com/post/fake-solidity-vscode-extension-on-open-vsx-used-to-backdoor-blockchain-developers-and-steal-cryptocu)
9. [SaaS Supply Chain Attacks: MITRE ATT&CK](https://appomni.com/blog/saas-supply-chain-attacks-mitre-attck-mapping/)
10. [Deliver Uncompromised: Securing Critical Software Supply ...](https://www.mitre.org/sites/default/files/2021-11/prs-21-0278-deliver-uncompromised-securing-critical-software-supply-chain.pdf)
11. [MITRE ATT&CK: Software](https://attack.mitre.org/software/)
12. [MITRE ATT&CK: Supply chain compromise](https://www.infosecinstitute.com/resources/mitre-attck/mitre-attck-supply-chain-compromise/)
13. [Malicious VSX Extension "SleepyDuck" Uses Ethereum to ...](https://radar.offseq.com/threat/malicious-vsx-extension-sleepyduck-uses-ethereum-t-2ecf319c)
14. ['GlassWorm' Malware Infects VS Code Extensions](https://dailysecurityreview.com/cyber-security/application-security/supply-chain-attack-glassworm-malware-infects-vs-code-extensions/)
15. ["SleepyDuck" uses Ethereum, SesameOp abuses OpenAI ...](https://www.youtube.com/watch?v=e0gXg2AQUSk)
16. [The State of Software Supply Chain Security Risks](https://www.blackduck.com/content/dam/black-duck/en-us/reports/state-of-software-supply-chain-security-risks-ponemon.pdf)
17. [NIST CSF 2.0: Updated Third Party & Supply Chain Risk Management](https://blog.riskrecon.com/nist-csf-2.0-updated-third-party-supply-chain-risk-management-part-2)
18. [Table1 - NIST Computer Security Resource Center](https://csrc.nist.gov/files/pubs/shared/docs/NIST-Cybersecurity-Publications.xlsx)
19. [Defending Against Software Supply Chain Attacks - CISA](https://www.cisa.gov/sites/default/files/publications/defending_against_software_supply_chain_attacks_508.pdf)
20. [Enhancing Software Supply Chain Security with NIST CSF 2.0](https://www.youtube.com/watch?v=7t7sI2PglTo)
21. [Defending Against Software Supply Chain Attacks - Hyperproof](https://hyperproof.io/resource/software-supply-chain-attacks/)