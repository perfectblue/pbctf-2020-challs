#pragma once

#include <stdint.h>
//#include <stdio.h>

template <unsigned int N>
struct _Bignum
{
    typedef _Bignum<N> Word;
    typedef _Bignum<N/2> Half;
    Half lo;
    Half hi;

    __forceinline _Bignum(const Half lo, const Half hi) : lo(lo), hi(hi)
    {
    }

    template <typename THalf>
    __forceinline _Bignum(const THalf lo) : lo(lo), hi()
    {
    }

    __forceinline _Bignum() : lo(), hi()
    {
    }


    //__forceinline Word operator=(const Word& other)
    //{
    //    this->lo = other.lo;
    //    this->hi = other.hi;
    //    return *this;
    //}

    __forceinline _Bignum<N*2> operator*(const Word& other) const
    {
        const Half& u1 = this->lo;
        const Half& v1 = other.lo;
        Word t = (u1 * v1);
        const Half& w3 = t.lo;
        const Half& k = t.hi;

        const Half& op1 = this->hi;
        Word t2 = (op1 * v1) + k;
        const Half& k2 = t2.lo;
        const Half& w1 = t2.hi;

        const Half& op2 = other.hi;
        Word t3 = (u1 * op2) + k2;
        const Half& k3 = t3.hi;

        Word big_hi = (op1 * op2) + w1 + k3;
        Word big_lo = Word(w3, t3.lo);
        return _Bignum<N*2>(big_lo, big_hi);
    }

    __forceinline Word operator+(const Half& other) const
    {
        return (*this + (Word) other).lo;
    }

    __forceinline _Bignum<N*2> operator+(const Word& other) const
    {
        Word sum_lo = this->lo + other.lo;
        Word sum_hi = this->hi + other.hi;
        Word mid = sum_lo.hi + sum_hi.lo;
        Word big_lo = Word(sum_lo.lo, mid.lo);
        Word big_hi = sum_hi.hi + mid.hi;
        return _Bignum<N*2>(big_lo, big_hi);
    }

    __forceinline Word operator>>(int n) const
    {
        if (n == N/2)
        {
            return Word(this->hi, Half());
        }
        else if (n > N / 2)
        {
            Half lo = this->hi >> (n - N/2);
            Half hi = Half();
            return Word(lo, hi);
        }
        else
        {
            Half lo = (this->lo >> n) | (this->hi << (N / 2 - n));
            Half hi = this->hi >> n;
            return Word(lo, hi);
        }
    }

    __forceinline Word operator<<(int n) const
    {
        if (n == N/2)
        {
            return Word(Half(), this->lo);
        }
        else if (n > N / 2)
        {
            Half lo = Half();
            Half hi = this->lo << (n - N / 2);
            return Word(lo, hi);
        }
        else
        {
            Half lo = this->lo << n;
            Half hi = (this->hi << n) | (this->lo >> (N / 2 - n));
            return Word(lo, hi);
        }
    }

    __forceinline Word operator|(const Word& other) const
    {
        return Word(this->lo | other.lo, this->hi | other.hi);
    }

    __forceinline Word operator&(const Word& other) const
    {
        return Word(this->lo & other.lo, this->hi & other.hi);
    }

    __forceinline Word operator~() const
    {
        return Word(~this->lo, ~this->hi);
    }

    __forceinline Word operator-() const
    {
        Half fuck = Half(1);
        Word a = ~*this;
        return a + fuck;
    }

    __forceinline operator _Bignum<N*2>() const
    {
        return _Bignum<N*2>(*this, 0);
    }

    //__forceinline void print() const
    //{
    //    hi.print();
    //    lo.print();
    //}
};

template <>
struct _Bignum<16>
{
    typedef _Bignum<16> Word;

    uint16_t value;

    __forceinline _Bignum(uint16_t scalar) : value(scalar)
    {
    }

    __forceinline _Bignum() : value(0)
    {
    }

    __forceinline _Bignum<32> operator*(const Word& other) const
    {
        uint32_t product = (uint32_t)this->value * (uint32_t)other.value;
        return _Bignum<32>(product & 0xffff, product >> 16);
    }

    __forceinline _Bignum<32> operator+(const Word& other) const
    {
        uint32_t sum = (uint32_t)this->value + (uint32_t)other.value;
        return _Bignum<32>(sum & 0xffff, sum >> 16);
    }

    __forceinline operator _Bignum<32>() const
    {
        return _Bignum<32>(this->value, (uint16_t)0);
    }

    __forceinline Word operator|(const Word& other) const
    {
        return Word(this->value | other.value);
    }

    __forceinline Word operator&(const Word& other) const
    {
        return Word(this->value & other.value);
    }

    __forceinline Word operator~() const
    {
        return Word(~this->value);
    }

    __forceinline Word operator-() const
    {
        return Word(-this->value);
    }

    __forceinline Word operator>>(int n) const
    {
        return Word(this->value >> n);
    }

    __forceinline Word operator<<(int n) const
    {
        return Word(this->value << n);
    }

    //__forceinline void print() const
    //{
    //    printf("%08x", value);
    //}
};

typedef _Bignum<16> Bignum16;
typedef _Bignum<32> Bignum32;
typedef _Bignum<64> Bignum64;
typedef _Bignum<128> Bignum128;
typedef _Bignum<256> Bignum256;
typedef _Bignum<512> Bignum512;
typedef _Bignum<1024> Bignum1024;

__forceinline static Bignum32 from32(uint32_t x)
{
    return Bignum32(x & 0xffff, x >> 16);
}

__forceinline static Bignum64 from64(uint64_t x)
{
    return Bignum64(from32(x & 0xffffffff), from32(x >> 32));
}

__forceinline static Bignum128 from128(uint64_t a, uint64_t b)
{
    return Bignum128(from64(a), from64(b));
}

// a = lowest, d = highest
__forceinline static Bignum256 from256(uint64_t a, uint64_t b, uint64_t c, uint64_t d)
{
    return Bignum256(from128(a, b), from128(c, d));
}

