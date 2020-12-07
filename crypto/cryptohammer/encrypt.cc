#include <sys/random.h>
#include <cstdio>

template <int N>
struct CSPRNG {
	CSPRNG()
	{
		m_ofs = 0;
		getrandom(m_key, sizeof m_key, GRND_NONBLOCK);
		getrandom(m_state, sizeof m_state, GRND_NONBLOCK);
	}
	char next()
	{
		char o = 0;
		for (int i = 0; i < N; i++) {
			o ^= m_state[(m_ofs+i)%N]&m_key[(i)%N];
		}
		m_state[m_ofs++] = o;
		m_ofs = (m_ofs+1)%N;
		return o;
	}
private:
	char m_key[N];
	char m_state[N];
	int m_ofs;
};

int main()
{
	CSPRNG<40000> p;
	int c;
	while ((c=getchar())+1) {
		putchar(c^p.next());
	}
	return 0;
}
