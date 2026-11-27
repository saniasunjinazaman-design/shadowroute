# Project Shadow Route

**BGP Prefix-Origin Hijack Detection and Prefix Filtering in a Controlled SEED Emulator Lab**

Project Shadow Route demonstrates a controlled route-origin hijack in a five-AS virtual lab, detects an unexpected origin at AS152, and uses an exact-prefix BIRD import filter at AS3 to reject the tested route from AS151.

> This repository is for an isolated educational lab. Do not apply the supplied route configuration to networks you do not own or administer. The attack configuration intentionally uses a blackhole route and can interrupt traffic inside the lab.

## Lab topology

| AS | Lab role | Expected relationship |
|---|---|---|
| AS150 | Legitimate origin of `10.150.0.0/24` | Transit via AS2 |
| AS151 | Controlled test announcer | Peers with AS3 |
| AS2 | Transit | Connects AS150 to AS3 |
| AS3 | Transit and filtering AS | Rejects the tested prefix from AS151 when the filter is enabled |
| AS152 | Observer | Runs the detector against its selected route |
| IX100 | Shared exchange network | Connects the lab routers |

At AS152, the normal selected AS path is `3 2 150`. During the recorded controlled hijack it was `3 151`. The detector compares the final AS number in the selected AS path to the trusted baseline AS150. A mismatch creates `HIJACK_ALERT`; the detector itself does not change routes.

## What is included

- `topology/shadow_route.py` — SEED Emulator five-AS topology definition.
- `detector/detector.py` — selected-route parser, origin comparison, JSONL event logging.
- `dashboard/app.py` — read-only Streamlit monitor with route status, topology, peer state, event history, evaluation view, and optional gallery.
- `filters/as3_prefix_filter.conf` — complete AS3 lab configuration with the `c_as151` exact-prefix filter enabled.
- `backups/as3_before_filter.conf` — reconstructed AS3 baseline configuration for the lab.
- `attack/as151_hijack.conf` — complete AS151 lab configuration with the controlled blackhole announcement enabled.
- `backups/as151_before_hijack.conf` — AS151 baseline configuration for restoration.
- `evaluation/` and `evidence/evaluation/` — analysis script and five recorded timing rows.
- `tests/test_detector.py` — six parser unit tests.
- `presentation/` — the supplied project presentation.

## Requirements

- Ubuntu 20.04 SEED VM or a compatible Linux lab host
- Docker and Docker Compose
- SEED Emulator Python environment
- BIRD 2.x in the generated router containers
- Python 3.11 recommended for the supplied environment

The SEED Emulator source is an external dependency and is not copied into this repository. Set `SEED_EMULATOR_DIR` if it is not at `./seed-emulator`.

## Setup

1. Clone this repository on the lab VM and enter it:

   ```bash
   git clone <your-repository-url> ShadowRoute
   cd ShadowRoute
   ```

2. Obtain the SEED Emulator separately, then install its documented dependencies. Set its location if needed:

   ```bash
   export SEED_EMULATOR_DIR="$PWD/seed-emulator"
   ```

3. Generate the Docker lab configuration. This step generates files; it does not start the containers:

   ```bash
   python3 topology/shadow_route.py
   ```

4. Build and start the generated lab from `shadow-output/` using the Docker Compose version installed on your SEED VM. For example:

   ```bash
   cd shadow-output
   sudo docker-compose up -d
   sudo docker-compose ps
   cd ..
   ```

5. Install Python dependencies in the project environment:

   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   If your SEED Emulator setup requires using its existing virtual environment, use that environment instead.

## Run the dashboard

From the repository root:

```bash
streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501
```

Open `http://<SEED-VM-host-only-IP>:8501` from a browser that can reach the VM. The page refreshes every two seconds. It is read-only and requires Docker access to inspect BIRD.

The dashboard has a sign-up tab for local lab accounts. An optional administrator login can be configured with `SHADOW_USER` and `SHADOW_PASS` environment variables. There is no default admin password. Keep real credentials private and never commit `.env` or `users.json`.

## Controlled demonstration

Keep the lab isolated. Confirm the container names match your generated Compose project before running these commands.

### 1. Confirm the normal route

```bash
sudo docker exec as152brd-router0-10.152.0.254 birdc show route all | grep -A7 '10.150.0.0/24'
python detector/detector.py --once
```

Expected route: `BGP.as_path: 3 2 150`; expected detector state: `NORMAL`.

### 2. Temporarily remove the AS3 filter

```bash
sudo docker cp backups/as3_before_filter.conf as3brd-router0-10.3.0.254:/etc/bird/bird.conf
sudo docker exec as3brd-router0-10.3.0.254 birdc configure
```

### 3. Activate the controlled AS151 announcement

The included file is a complete lab BIRD configuration based on the supplied AS151 baseline plus the controlled blackhole announcement. It is specific to this generated topology.

```bash
sudo docker cp attack/as151_hijack.conf as151brd-router0-10.151.0.254:/etc/bird/bird.conf
sudo docker exec as151brd-router0-10.151.0.254 birdc configure
sleep 5
python detector/detector.py --once
```

Expected detector status when the route is selected: `HIJACK_ALERT`, with observed origin `151` and path `[3, 151]`. The dashboard should show the same state.

### 4. Mitigate and restore the legitimate route

Load the included complete AS3 lab configuration, which adds the exact-prefix reject rule to the `c_as151` import filter:

```bash
sudo docker cp filters/as3_prefix_filter.conf as3brd-router0-10.3.0.254:/etc/bird/bird.conf
sudo docker exec as3brd-router0-10.3.0.254 birdc configure
sleep 5
sudo docker exec as152brd-router0-10.152.0.254 birdc show route all | grep -A7 '10.150.0.0/24'
python detector/detector.py --once
```

Expected final state: selected path returns to `3 2 150`; detector reports `NORMAL`. The filter performs mitigation; the detector reports the route change; the dashboard displays both states.

### 5. Restore the attacker router and verify connectivity

```bash
sudo docker cp backups/as151_before_hijack.conf as151brd-router0-10.151.0.254:/etc/bird/bird.conf
sudo docker exec as151brd-router0-10.151.0.254 birdc configure
sudo docker exec as152h-host0-10.152.0.71 ping -c 4 10.150.0.71
```

## Evaluation

Five recorded detection times: **0.895, 1.122, 0.995, 0.969, and 1.248 seconds**. Mean: **1.046 s**; median: **0.995 s**; sample standard deviation: **0.140 s**. Timing is measured from attack configuration reload to detector observation and includes route propagation and one-second polling. It is specific to this VM lab and is not a production-network claim.

To regenerate the summary and chart:

```bash
python evaluation/analyze_results.py
```

To run the parser unit tests:

```bash
python -m unittest discover -s tests -v
```

## Limitations

- Monitors one configured prefix and trusts a static origin baseline.
- Uses BIRD CLI output parsing; output changes may require parser updates.
- Uses one-second polling and only five recorded timing trials in one VM lab.
- Does not implement RPKI/ROA validation or automatic route blocking.
- The AS3 rule is an exact-prefix lab filter, not a full Internet routing-security solution.

## Public repository checklist

- Do not upload `.env`, `users.json`, VM credentials, or personal access tokens.
- Do not include generated Docker image layers or the entire SEED Emulator dependency unless its license and size are checked.
- Review screenshots and logs for personal information before adding them.
- Keep the experiment results and their lab-only scope together.
