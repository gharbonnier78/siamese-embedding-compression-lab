# PC-side digital twin — executable, synthetic only

The laboratory PC can simulate **what the external supervisory/analysis station would see** before any hardware is built.

## Scope

- Synthetic descriptors for nominal visible RGB, NIR night, backlight/oblique pose, motion blur, partial occlusion, wet-window scenario and empty passage. **These are condition tags and deterministic invented vectors, NOT actual RGB/NIR pixels or a trained model.**
- Exactly **one active representation per simulated run**: 512D or 128D.
- Exact synthetic nearest-neighbour scores and **simulated** allowlist candidate / watchlist review request / unknown / no-decision handling; no automatic exclusion or real identity claim.
- Assumed per-mode watts, ambient/case temperatures and battery state of charge, clearly labeled ASSUMED; these are *NOT* calibrated probe readings.
- Virtual Ethernet status and separate low-power alert-radio status, queuing when disconnected, network ACK distinct from human ACK.
- External PC dashboard on 127.0.0.1, using **loopback HTTP only** as a controlled demonstration of the Ethernet interface; it cannot be used in production and does not implement real network authentication or mTLS.
- Encrypted research evidence vault prototype and signed single-active-model package in sibling folders. Any real face data requires separate approval, protected storage and acquisition tooling.

## Now implemented: deterministic **image-pixel** comparison

The previous control-flow twin below remains synthetic scene metadata. The **new** [Pixel Replay module](PIXEL_REPLAY_AND_MODEL_ADAPTERS.md) instead generates actual files containing **non-human abstract RGB-like/NIR-like patterns**, reads their pixels with Pillow, extracts a deterministic DCT512 vector and compares exact 512D versus an orthogonal random128 projection on **identical images**. This is NOT a trained face recognizer or real NIR optical sensing. Run `python engineering/sim/pixel_replay.py --out /tmp/siamese-pixel-demo`, then open its local HTML dashboard. True authorized RGB/NIR paired captures and trained models still require separate protected adapters.

## Run locally

From repository root:

\`\`\`bash
python -m pip install -r engineering/requirements.txt
python engineering/sim/bench.py --seed 7 --samples 120 --output /tmp/sim-power
python engineering/sim/digital_twin.py --dim 128 --out /tmp/siamese-twin-128
python engineering/sim/digital_twin.py --dim 512 --out /tmp/siamese-twin-512
python engineering/sim/digital_twin.py --dim 128 --ethernet-down --rf-down --out /tmp/siamese-twin-offline
python -m unittest discover -s engineering/sim/tests -v
\`\`\`

Then open a separate terminal and start the local PC console:

\`\`\`bash
export SIAMESE_DEMO_CONSOLE_TOKEN="$(python -c 'import secrets;print(secrets.token_urlsafe(32))')"
python engineering/sim/console.py --port 8765
\`\`\`

In a second terminal using **the same** environment token:

\`\`\`bash
python engineering/sim/digital_twin.py --dim 128 \
  --out /tmp/siamese-twin-128 \
  --demo-console http://127.0.0.1:8765 \
  --demo-token "$SIAMESE_DEMO_CONSOLE_TOKEN"
\`\`\`

Open \`http://127.0.0.1:8765\` on the **same PC**. You should see the simulated probe table, active embedding dimension, Ethernet status and short alert/ACK records. The demo console binds only to loopback and intentionally rejects data not marked synthetic.

## Real visual RGB/NIR replay — later, not assumed

Our mock scene descriptors are a **dry run of the data/decision flow**. For real paired images, choose data with documented license, lawful collection/retention and appropriate scene conditions, including same-subject RGB/NIR pairs and pose/environment metadata. Keep sensitive imagery entirely outside GitHub, Flux and cloud CI. After legal/data clearance, implement camera acquisition and a plugin \`ImagePairReader → Quality/PAD → Extractor → Projection(512 or 128) → Index → Policy\`, bound to exact firmware/model/dataset hashes. Full-acquisition recordings are encrypted in a separate controlled vault; no casual recording of all attendees.

Replaying the same saved video/photos can compare model outputs on identical pixels, but **cannot** prove how a new lens/sensor will behave in rain/sun or how much energy a different capture would have consumed. Those are separate physical experiments.

## Still missing before real-world use

Real camera drivers; synchronized NIR hardware capture; target SoM model runtime and validated NPU/GPU; operator access control and lawful user list management; vetted TLS+mTLS, secure provisioning, local encryption, real instrument drivers, RF link budget and measured power/thermal; reproducible trial with a qualified data set. This is an engineering starting point, NOT a security appliance.
## Roadmap for actual RGB/NIR portraits

For a separate offline, access-controlled next phase, see [IMAGE_PAIR_REPLAY_PLAN.md](IMAGE_PAIR_REPLAY_PLAN.md). The present synthetic scene simulator uses **no image pixels**, while the planned image-pair adapter requires real, licensed/consented simultaneous RGB+NIR capture and controlled access; converting RGB with a grayscale filter is **not** physically equivalent to NIR. The plan maps all scenes (frontal/profile, backlit, low-light, wet-window, movement) to the 128D/512D frozen-model replay and to the PC supervisor, and explicitly separates control-flow mocks, real offline images, and physical measurement.
