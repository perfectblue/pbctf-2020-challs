# Too Structured

**Category**: Crypto

**Author**: braindead

**Description**: null

**Public files**: 
 * dist/public_key
 * dist/flag.txt.enc
 * dist/challenge.sage

**Distribute**:
 * dist/deliverables/toostructured.zip

## Solution
This is an insecure variation of McEliece's cryptosystem with Generalized Reed
Solomon codes instead of Goppa codes. Private key can be recovered using the
attack described in SS.pdf To solve this you also need to decode GRS codes,
which is described in GRS.pdf

Full solution script is in solution.sage, it should recover the flag in under a
minute.

***** pbctf{McEl13c3_W1th_RE3d_soLOM0n_is_N0t_bu3n0Oo}
