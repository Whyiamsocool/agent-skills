# Document Analysis Guide

This guide provides patterns and best practices for analyzing different document types against reference sources.

## Analysis Workflow

### 1. Document Understanding Phase
- Extract and review document structure (sections, headings, length)
- Identify document type and purpose
- Note key topics and coverage areas
- Understand intended audience and scope

### 2. Reference Selection Phase
- Extract keywords and themes from document
- Match against available NotebookLM notebooks
- Rank notebooks by relevance
- Select most relevant sources (typically 1-3 notebooks)

### 3. Requirements Extraction Phase
- Query selected notebooks for comprehensive requirements
- For detailed analysis: query each major section/category separately
- For quick analysis: query for high-level requirements summary
- Document all source requirements with citations

### 4. Comparison Phase
- Map document sections to requirement categories
- Identify what's covered and what's missing
- Assess quality of coverage (complete, partial, inadequate)
- Note areas of strength and weakness

### 5. Report Generation Phase
- Compile findings based on output options (gap/alignment/recommendations)
- Prioritize gaps by severity (critical, high, medium, low)
- Provide actionable recommendations with specific references
- Format report for clarity and usability

## Document Type Patterns

### Compliance Policies
**Characteristics:** Formal internal policies governing regulatory compliance

**Analysis Focus:**
- Regulatory requirement coverage (are all legal obligations addressed?)
- Internal control procedures (are processes documented?)
- Roles and responsibilities (are owners clearly defined?)
- Monitoring and reporting (are oversight mechanisms in place?)

**Common Gaps:**
- Missing specific thresholds or quantitative requirements
- Vague procedures without clear step-by-step guidance
- Inadequate documentation of exception handling
- Missing links between policy and operational procedures

**Query Strategy:**
- Query for comprehensive regulatory requirements by category
- Ask for specific obligations (thresholds, timelines, reporting)
- Inquire about enforcement and audit requirements

### Operational Procedures
**Characteristics:** Step-by-step instructions for executing specific processes

**Analysis Focus:**
- Completeness of steps (are all required actions documented?)
- Technical accuracy (do procedures align with best practices?)
- Exception handling (what happens when things go wrong?)
- Integration points (how does this connect to other processes?)

**Common Gaps:**
- Missing error handling and escalation procedures
- Lack of validation checkpoints
- Insufficient detail on technical implementation
- No documentation of system/tool requirements

**Query Strategy:**
- Query for detailed procedural requirements
- Ask for best practices and common pitfalls
- Inquire about technical standards and specifications

### Business Proposals
**Characteristics:** Documents proposing new initiatives, projects, or business activities

**Analysis Focus:**
- Regulatory compliance considerations (are legal requirements addressed?)
- Risk assessment (are risks identified and mitigated?)
- Stakeholder requirements (are all parties' needs considered?)
- Implementation feasibility (is the approach practical?)

**Common Gaps:**
- Incomplete risk analysis
- Missing regulatory approval requirements
- Inadequate resource planning
- Lack of success metrics and monitoring

**Query Strategy:**
- Query for regulatory approval requirements
- Ask for risk factors and mitigation strategies
- Inquire about industry best practices

### Contracts and Agreements
**Characteristics:** Legal documents establishing rights and obligations

**Analysis Focus:**
- Legal requirement compliance (mandatory clauses, disclosures)
- Standard terms and conditions (industry-standard provisions)
- Risk allocation (liability, indemnification, warranties)
- Regulatory mandates (required contractual terms)

**Common Gaps:**
- Missing required regulatory clauses
- Inadequate liability provisions
- Vague performance standards or SLAs
- Insufficient termination and dispute resolution terms

**Query Strategy:**
- Query for mandatory contractual provisions
- Ask for regulatory disclosure requirements
- Inquire about standard industry terms

### Technical Documentation
**Characteristics:** Documentation of systems, architectures, or technical implementations

**Analysis Focus:**
- Technical standard compliance (industry standards, protocols)
- Security and privacy requirements (regulatory mandates)
- Integration requirements (compatibility, interoperability)
- Operational requirements (monitoring, maintenance, support)

**Common Gaps:**
- Missing security controls and privacy measures
- Inadequate disaster recovery and business continuity
- Lack of monitoring and alerting specifications
- Insufficient documentation of dependencies

**Query Strategy:**
- Query for technical standards and specifications
- Ask for security and privacy requirements
- Inquire about operational best practices

## Depth Levels

### Quick Review
**Time:** 5-10 minutes
**Output:** High-level summary with top 3-5 findings

**Process:**
1. Extract document keywords
2. Select 1-2 most relevant notebooks
3. Query for high-level requirements summary
4. Identify 3-5 most critical gaps or risks
5. Generate quick summary report

**Best for:**
- Initial assessment before detailed review
- Executive briefings
- Prioritization decisions

### Detailed Review
**Time:** 30-60 minutes
**Output:** Comprehensive gap analysis, alignment summary, and recommendations

**Process:**
1. Extract and analyze full document structure
2. Select all relevant notebooks (typically 1-3)
3. Query each notebook for comprehensive requirements by category
4. Perform section-by-section comparison
5. Categorize findings by severity and type
6. Generate full report with all sections

**Best for:**
- Formal compliance reviews
- Document updates and revisions
- Audit preparation
- Regulatory submissions

## Severity Classification

### Critical
- Legal/regulatory violations
- Missing mandatory requirements
- High financial or reputational risk
- Immediate action required

### High
- Best practice gaps with significant risk
- Incomplete coverage of important requirements
- Potential regulatory scrutiny
- Should be addressed soon

### Medium
- Areas for improvement without immediate risk
- Partial coverage that could be enhanced
- Industry standard practices not fully adopted
- Should be addressed in next update cycle

### Low
- Minor enhancements
- Documentation improvements
- Clarifications and formatting
- Nice-to-have improvements

## Recommendation Guidelines

### Good Recommendations Are:
- **Specific:** Clearly state what needs to be added/changed
- **Actionable:** Provide concrete steps to address the gap
- **Referenced:** Cite the source requirement or standard
- **Prioritized:** Indicate relative importance and urgency
- **Contextual:** Explain why the change matters

### Example Good Recommendation:
```
Add explicit transaction monitoring thresholds section specifying $1,000 threshold for digital asset transfers requiring Travel Rule compliance (POCR Regulation 10, BMA DAB Guidance Section 4.2). This is critical to prevent structuring violations and ensure regulatory compliance.
```

### Example Poor Recommendation:
```
Improve transaction monitoring section.
```

## Multi-Notebook Analysis

When multiple relevant notebooks are identified:

1. **Query each notebook separately** for requirements
2. **Consolidate requirements** by category across sources
3. **Identify overlaps** and note where sources agree/differ
4. **Prioritize** requirements from most authoritative sources
5. **Cross-reference** to ensure complete coverage

**Example:**
If analyzing a compliance policy against both "Bermuda AML Regulations" and "FATF AML Standards":
- Query Bermuda regulations for local legal requirements (highest priority)
- Query FATF standards for international best practices
- Note where Bermuda implements FATF recommendations
- Identify gaps in both local law and international standards
