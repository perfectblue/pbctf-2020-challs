# Jiang Ying's Disassembler

**Category**: Reversing

**Author**: cts

**Description**:

Come on, this should be easy. It even has the PDB. Let's make a keygen.

`nc ctf.perfect.blue 12341234`

**Remote**:
 - Deploy remote.py in xinetd style.
 - It needs to be run with `python3 -u` like in the shebang
 - Depends on Pycryptodome

**Public files**: 
 * dist.7z

## Solution
The binary implements 128-bit RSA in a horrible fashion using C++ templates.
Specifically, it uses templates to construct BigNums out of smaller BigNums. The base BigNum size is 32-bit, so all operations boil down to 32-bit machine arithmetic.

RSA parameters:
- n = 303111819233903650638787601663617221623
- e = 17
- d = 53490321041277114812464604913116260313

To check if a license (jda.key) is valid, the first 16 bytes are a signature that is a 128-bit integer. The rest of the file is hashed with sha256. The 128-bit integer signature is then multiplied by 0x7287472427975c62eb7fd64e061c1a3d = 123456789^-1. This is just to prevent some trivial black-box attacks by guess gods. Then it's encrypted with RSA and checked against the first 16 bytes of the hash. So to generate valid keys, you need to break the RSA. Also, if the hash is greater than modulus, you need to change up the data and try again.

The N is very small (128 bits) and can be factored quickly using brute force.

See `solve.py`.
