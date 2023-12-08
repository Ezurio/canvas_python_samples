# Scanning Examples.

## Overview.
These examples demonstrate how to perform general and filtered scans.


## Description
### simple_scan.py
- Initiates a simple scan. Uses the callback mechanism to display details of any device it scans. After a time period it will stop the scan.

### simple_scan_filter.py and scan_filter_advert.py
- scan_filter_advert.py simply starts an advert with a particular name / byte pattern in the full advert name section.
- simple_scan_filter.py Sets up a filter uing the same byte pattern. Any received adverts will only be reported via the callback if they contain this byte pattern.


## Other Requirements
None
