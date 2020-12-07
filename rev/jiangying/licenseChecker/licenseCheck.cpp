#include <stdint.h>
#include <string.h>

#include "licenseCheck.h"
#include "rsa.h"
#include "integer.h"
#include "sha256.h"

void ProcessKey(uint8_t* keyIn, uint8_t* keyOut)
{
	uint64_t lo = *(uint64_t*)(keyIn + 0);
	uint64_t hi = *(uint64_t*)(keyIn + 8);
	auto m = from128(lo, hi);
	m = (m * from128(0xeb7fd64e061c1a3d, 0x7287472427975c62)).lo; // 0x7287472427975c62eb7fd64e061c1a3d = 123456789^-1 mod 2^128
	auto c = pow_e_n(m);
	//for i in range(8): print ('*(uint16_t*)(keyOut + %d) = c' % (2*i,) + bin(i)[2:].zfill(3).replace('0','.lo').replace('1','.hi') + '.value;')
	*(uint16_t*)(keyOut + 0) = c.lo.lo.lo.value;
	*(uint16_t*)(keyOut + 2) = c.lo.lo.hi.value;
	*(uint16_t*)(keyOut + 4) = c.lo.hi.lo.value;
	*(uint16_t*)(keyOut + 6) = c.lo.hi.hi.value;
	*(uint16_t*)(keyOut + 8) = c.hi.lo.lo.value;
	*(uint16_t*)(keyOut + 10) = c.hi.lo.hi.value;
	*(uint16_t*)(keyOut + 12) = c.hi.hi.lo.value;
	*(uint16_t*)(keyOut + 14) = c.hi.hi.hi.value;
}

extern "C" bool CheckLicenseSignature(uint8_t* buf, int len)
{
	if (len < 16)
	{
		return false;
	}
	
	uint8_t hashCheck[16];
	ProcessKey(&buf[0], hashCheck);

	uint8_t hash[32];
	SHA256_CTX ctx;
	sha256_init(&ctx);
	sha256_update(&ctx, buf + 16, len - 16);
	sha256_final(&ctx, hash);

	//for (int i = 0; i < 16; i++) {
	//	printf("%02x ", hashCheck[i]);
	//}
	//printf("\n");
	//for (int i = 0; i < 16; i++) {
	//	printf("%02x ", hash[i]);
	//}
	//printf("\n");

	return !memcmp(hashCheck, hash, 16);
}