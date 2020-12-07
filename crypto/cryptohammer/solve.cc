#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <algorithm>
#include <vector>
#include <iostream>
#include <fstream>
#include <limits.h>
#include <math.h>
#include <unordered_map>
#include <assert.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <err.h>

using std::vector;
using u8 = uint8_t;

#define ran(i, a, b) for (auto (i) = (a); (i) < (b); (i)++)
#define DEBUG(...) std::cerr << __VA_ARGS__ << std::endl;
#ifndef ENABLE_DEBUG
#undef DEBUG
#define DEBUG(...) ((void)0)
#define NDEBUG
#endif
#define INFO(...) std::cerr << "[*] " << __VA_ARGS__ <<std::endl;

static const int MAX = 3010;

template <typename T, T P>
struct intmod {
	intmod() {}
	constexpr intmod(T t) : x((t+P)%P) {}
	T value() const { return x; }
	bool operator!=(const intmod<T, P> i) { return x != i.x; }
	bool operator==(const intmod<T, P> i) { return x == i.x; }
	intmod<T, P> &operator+=(const intmod<T, P> i) { x = (x+i.x)%P; return *this; }
	intmod<T, P> &operator-=(const intmod<T, P> i) { x = (x+P-i.x)%P; return *this; }
	intmod<T, P> &operator*=(const intmod<T, P> i) { x = ((long long)x*i.x)%P; return *this; }
	intmod<T, P> &operator/=(const intmod<T, P> i) { x = ((long long)x*i.inverse().x)%P; return *this; }
	intmod<T, P> operator+(const intmod<T, P> i) const { auto j = *this; return j += i; }
	intmod<T, P> operator-(const intmod<T, P> i) const { auto j = *this; return j -= i; }
	intmod<T, P> operator*(const intmod<T, P> i) const { auto j = *this; return j *= i; }
	intmod<T, P> operator/(const intmod<T, P> i) const { auto j = *this; return j /= i; }
	intmod<T, P> operator-() const { intmod<T, P> n; n.x = (P-x)%P; return n; }
	intmod<T, P> inverse() const
	{
		if (x == 0)
			return 0;
		T a = x, b = P;
		T aa = 1, ab = 0;
		T ba = 0, bb = 1;
		while (a) {
			T q = b/a;
			T r = b%a;
			ba -= aa*q;
			bb -= ab*q;
			std::swap(ba, aa);
			std::swap(bb, ab);
			b = a;
			a = r;
		}
		intmod<T, P> ix = intmod<T, P>(aa) + intmod<T, P>(ba);
		assert(ix*x == unity);
		return ix;
	}
	static const intmod<T, P> zero;
	static const intmod<T, P> unity;
private:
	T x;
};
template <typename T, T P>
constexpr intmod<T, P> intmod<T, P>::zero = 0;
template <typename T, T P>
constexpr intmod<T, P> intmod<T, P>::unity = 1;

using rem = intmod<char, 2>;

template <typename K>
static vector<K> berlekamp_massey(vector<K> ss)
{
	vector<K> ts(ss.size());
	vector<K> cs(ss.size());
	cs[0] = K::unity;
	fill(cs.begin()+1, cs.end(), K::zero);
	vector<K> bs = cs;
	int l = 0;
	int m = 1;
	K b = K::unity;
	for (int k = 0; k < (int)ss.size(); k++) {
		K d = ss[k];
		assert(l <= k);
		for (int i = 1; i <= l; i++)
			d += cs[i]*ss[k-i];
		if (d == K::zero) {
			m++;
		} else if (2*l <= k) {
			K w = d/b;
			ts = cs;
			for (int i = 0; i < (int)cs.size()-m; i++)
				cs[i+m] -= w*bs[i];
			l = k+1-l;
			swap(bs, ts);
			b = d;
			m = 1;
		} else {
			K w = d/b;
			for (int i = 0; i < (int)cs.size()-m; i++)
				cs[i+m] -= w*bs[i];
			m++;
		}
		//cerr << "order " << l << "/" << k << endl;
	}
	cs.resize(l+1);
	while (cs.back() == K::zero)
		cs.pop_back();
	return cs;
}

static int n;

namespace poly {
	template <typename K>
	void mul(vector<K> &dest, const vector<K> &l, const vector<K> &r)
	{
		int ln = l.size();
		int rn = r.size();
		int dn = ln+rn-1;
		dest.resize(dn, K::zero);
		ran (i, 0, ln)
		ran (j, 0, rn)
			dest[i+j] += l[i] * r[j];
	}

	template <typename K>
	K eval(const vector<K> &poly, rem x)
	{
		int n = poly.size();
		rem acc = K::zero;
		for (int i = n-1; i >= 0; i--) {
			acc = acc*x + poly[i];
		}
		return acc;
	}

	template <typename K>
	K eval_d(const vector<K> &poly, rem x)
	{
		int n = poly.size();
		rem acc = K::zero;
		for (int i = n-1; i > 0; i--) {
			acc = acc*x + rem(i)*poly[i];
		}
		return acc;
	}
};

template <typename K>
std::ostream &operator<<(std::ostream &o, const vector<K> &poly)
{
	o << "{";
	int n = poly.size();
	ran (i, 0, n-1)
		o << poly[i].value() << ", ";
	o << poly[n-1].value() << "}";
	return o;
}

int main()
{
	int fd = open("cryptohammer_40000/flag.iso.enc", O_RDONLY);
	if (fd < 0)
		err(1, "open");
	struct stat s;
	if (fstat(fd, &s) < 0)
		err(1, "stat");
	size_t n = s.st_size;
	u8 *enc = new u8[n];
	if (n != read(fd, enc, n))
		err(1, "read");
	close(fd);

	INFO("file size " << n);
	size_t probe_size = 100000;
	u8 *keystream = new u8[n];

	ran (i, 0, probe_size)
		keystream[n-probe_size+i] = enc[n-probe_size+i];

	ran (bitslice, 0, 8) {
		vector<rem> seq;
		ran (i, 0, probe_size)
			seq.push_back(keystream[n-probe_size+i]>>bitslice&1);
		vector<rem> recurence = berlekamp_massey(seq);
		INFO("bitslice " << bitslice << " order " << recurence.size());
		assert(recurence.back() == 1);
		assert(recurence.front() == 1);

		// validate the recurence
		ran (i, recurence.size(), seq.size()) {
			int bit = 0;
			ran (j, 0, recurence.size())
				bit ^= seq[i-j].value() & recurence[j].value();
			assert(bit == 0);
		}
		INFO("validated!");

		for (int i = n-probe_size-1; i >= 0; i--) {
			int bit = 0;
			ran (j, 0, recurence.size()-1)
				bit ^= (keystream[i+recurence.size()-1-j]>>bitslice&1) & recurence[j].value();
			keystream[i] |= bit<<bitslice;
		}
		INFO("recovered keystream");
	}

	u8 *txt = new u8[n];
	ran (i, 0, n)
		txt[i] = enc[i]^keystream[i];

	if ((fd = open("keystream.bin", O_WRONLY|O_TRUNC|O_CREAT, 0666)) < 0)
		err(1, "open");
	write(fd, keystream, n);
	close(fd);

	if ((fd = open("decrypted.iso", O_WRONLY|O_TRUNC|O_CREAT, 0666)) < 0)
		err(1, "open");
	write(fd, txt, n);
	close(fd);

	delete[] enc;
	delete[] keystream;
	delete[] txt;
	return 0;
}
