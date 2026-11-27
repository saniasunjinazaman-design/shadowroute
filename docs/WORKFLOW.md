# Project Workflow

1. Define the five-AS virtual topology with SEED Emulator.
2. Generate Docker router and host configurations.
3. Start the containers and establish BGP sessions using BIRD.
4. Confirm AS152 selects the legitimate AS150 route (`3 2 150`).
5. Run the Python detector against AS152's selected route.
6. In the isolated lab, allow AS151's controlled prefix announcement to reach AS152.
7. Compare the observed origin with the trusted AS150 baseline and display an alert.
8. Apply the AS3 import filter to reject the test prefix learned from AS151.
9. Confirm the legitimate path returns, the dashboard reports NORMAL, and host connectivity works.
10. Analyze the recorded timings and document the lab's limitations.
