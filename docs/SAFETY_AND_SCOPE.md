# Safety and Scope

This project is designed for a private, isolated SEED Emulator lab. The AS151 configuration includes a blackhole route for the victim prefix and can discard packets inside the lab. Use only the provided private lab topology. Never attach the test announcement to a public routing network.

The Python detector is read-only. It reports selected-route changes but does not block, rewrite, or withdraw routes. The AS3 BIRD import filter is the mitigation component. The dashboard displays state and does not apply routing changes.

The project is educational and has not been evaluated as a production security product.
