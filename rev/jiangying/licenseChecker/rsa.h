#pragma once

#include <stdint.h>
#include "integer.h"

/*
q = 17560823292485810621
p = 17260683863472602563
n = 303111819233903650638787601663617221623
e = 17
d = 53490321041277114812464604913116260313
n bits = 128
ring = Z_512
n^-1 = 0x8fb2557c2d290ff774305efb268fa71ba4ba7988b5d345c1f508052cb05b946c
n shift = 383
*/

__forceinline static Bignum128 mod_n(Bignum256 x)
{
	// quotient divide by N
	Bignum256 n_inv = from256(0xf508052cb05b946c, 0xa4ba7988b5d345c1, 0x74305efb268fa71b, 0x8fb2557c2d290ff7);
	Bignum256 q = ((x * n_inv) >> 383).lo;

	// remainder
	Bignum256 n = from256(0xf8af1eff84e143f7, 0xe4093681aa2b047a, 0, 0);
	Bignum256 r = (x + -(n * q).lo).lo;
	return r.lo;
}

__forceinline static Bignum128 pow_e_n(Bignum128 x)
{
	// e = 17
	// squaring
	auto x2 = mod_n(x * x);
	auto x4 = mod_n(x2 * x2);
	auto x8 = mod_n(x4 * x4);
	auto x16 = mod_n(x8 * x8);
	// x^17 = x^16 * x
	return mod_n(x16 * x);
}
