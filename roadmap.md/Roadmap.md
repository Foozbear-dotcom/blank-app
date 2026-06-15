# Sports Fixture Creation App Roadmap

Current Version
---------------
V1.6

Next
----
V1.6.1 Duplicate Seed Detection
V1.6.2 Missing Seed Detection
V1.6.3 Fixture vs Seedings Validation

## Completed

### V1.0
- Fixture Health Dashboard

### V1.1
- Missing Matchup Detection

### V1.2
- Venue Clash Detection

### V1.3
- Fixture Stage Selector

---

## Planned

### V1.4
- Venue Capacity By Round

### V1.5
- Home/Away Balance

### V1.6
- Seedings Upload

### V1.7
- Venue Configuration Improvements
V1.7   Venue Lookup Report
V1.7.1 Venue Exception Report
V1.7.2 Venue Return Framework
V1.7.3 Capacity Aware Venue Returns

### V1.8
- Download Reports (XLSX)
V1.8.1 Competition upload export
V1.8.2 Club view export
V1.8.3 XLSX multi-sheet export

### V1.9
- Export Fixture CSV
V1.9.1 - Override aware venue returns
V1.9.2 Override Assistant UI
- Select Venue Return Opportunity
- Show current venue usage
- Show games at default venue
- Override Reason dropdown
- Notes field
- Mark as Override
V1.9.3 Override-aware Export

# V2.0 Venue Change Reasons

Internal Reason
Public Reason
Included in Club Export
Included in Venue Change Summary

V2.0 Override Assistant UI
V2.0.1 Venue Evidence View
V2.0.2 Venue snapshot and override assistant improvements ***



### V3.0
- Draft Fixture Generator

V3.1 - Fixture Repair Assistant

Purpose:
Repair an existing fixture with the minimum possible disruption.

Inputs:
- Fixture
- Team constraints
- Bye targets
- Matchup targets
- Venue capacities
- Locked rounds

Outputs:
- Suggested repairs
- Number of rounds affected
- Teams affected
- Before/after comparison
- Repair score

Goals:
✓ Minimise rounds changed
✓ Minimise teams affected
✓ Preserve completed rounds
✓ Preserve locked games
✓ Restore fixture balance


---

## Ideas Parking Lot

- Team login access
- Club time allocation
- User workspaces
- Internal server deployment
- Audit reports
- Fixture health score
- Auto seeding suggestions
- Export Architecture
# V1.8 Data Rules

Rule 1:
Bye rows are fixture rows.

Rule 2:
Bye rows are not games.

Rule 3:
Capacity, venue and matchup calculations ignore Bye rows.

# Business Rules

Rule 1
Bye rows are fixture rows, not games.

Rule 2
Home venue comes from Seedings file.

Rule 3
Venue exceptions compare Default Venue to Current Venue.

Rule 4
Manual Overrides suppress venue return recommendations.

Rule 5
Capacity checks ignore Bye rows.