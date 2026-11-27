# Source Code Map

| Path | Purpose |
|---|---|
| `topology/shadow_route.py` | Defines AS150, AS151, AS2, AS3, AS152, IX100, and BGP peerings. |
| `detector/detector.py` | Reads AS152's selected route, extracts the origin, compares it with AS150, and records state changes. |
| `dashboard/app.py` | Read-only Streamlit interface for route state, peers, events, evaluation, and optional images. |
| `filters/as3_prefix_filter.conf` | Import-filter rule snippet for rejecting the test prefix from AS151 at AS3. |
| `attack/as151_hijack.conf` | Complete AS151 lab configuration with a static blackhole route used only in the controlled lab. |
| `backups/as151_before_hijack.conf` | AS151 configuration used to restore its baseline behavior. |
| `backups/as3_before_filter.conf` | AS3 baseline without the AS151 prefix reject rule. |
| `evaluation/analyze_results.py` | Computes summary statistics and exports a graph. |
| `tests/test_detector.py` | Parser cases for normal, hijack, missing, unselected, malformed, and missing-table output. |

The BIRD files under `attack/` and `filters/` are configuration snippets. Merge them into full generated router configurations; do not install a snippet as an entire `bird.conf`.
