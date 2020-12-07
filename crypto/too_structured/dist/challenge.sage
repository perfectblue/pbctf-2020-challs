from Crypto.Util.number import getRandomInteger, getRandomRange
from Crypto.Random import get_random_bytes
from Crypto.Cipher import ChaCha20
from hashlib import sha256

#################### utils ##########################################

def random_subset(lst, t):
	lst = list(lst)
	n = len(lst)
	for i in range(t):
		j = getRandomRange(i, n)
		lst[i], lst[j] = lst[j], lst[i]
	return lst[:t]

def random_choice(lst):
	return lst[getRandomRange(0, len(lst))]

def random_fullrank(ring, n):
	m = matrix.zero(ring, n, n)
	el = list(ring)
	while True:
		for i in range(n):
			for j in range(n):
				m[i,j] = random_choice(el)
		if m.rank() == n:
			return m

class BitWriter:
	def __init__(self):
		self._bytes = bytearray()
		self._buffer = 0
		self._buffer_len = 0

	def write(self, bits, n):
		self._buffer += bits<<self._buffer_len
		self._buffer_len += n
		while self._buffer_len >= 8:
			self._bytes.append(self._buffer&0xff)
			self._buffer >>= 8
			self._buffer_len -= 8

	def bytes(self): return self._bytes

#################### public key system ##############################

class Code:
	def __init__(self, n, k, field):
		self.n = n
		self.k = k
		self.field = field
		self.poly_ring = field['x']
		nz = list(self.field)
		nz.remove(self.field(0))
		self.a = random_subset(nz, self.n)
		self.z = [ random_choice(nz) for _ in range(n) ]

	def check_matrix(self):
		h = matrix.zero(Fq, k, n)
		for i in range(k):
			for j in range(n):
				h[i, j] = self.z[j] * self.a[j]^i
		return h

class KeyPair:
	def __init__(self, n, k, field):
		self.n = n
		self.k = k
		self.field = field
		self.gf_bits = log(field.order(), 2)

	def generate(n, k, field):
		self = KeyPair(n, k, field)
		self.code = Code(n, k, field)
		self.obfuscator = random_fullrank(field, k)
		self.check_matrix = self.obfuscator.inverse() * self.code.check_matrix()
		return self

	def public_key(self):
		pub = KeyPair(self.n, self.k, self.field)
		pub.check_matrix = self.check_matrix
		return pub

	def export_public(self):
		bw = BitWriter()
		for i in range(k):
			for j in range(n):
				bw.write(self.check_matrix[i,j].integer_representation(), self.gf_bits)
		return bw.bytes()

	def kem_encapsulate(self):
		e = [self.field(0)]*self.n
		nz = list(self.field)
		nz.remove(self.field(0))
		for i in random_subset(range(self.n), self.k//2):
			e[i] = random_choice(nz)

		bw = BitWriter()
		for i in range(self.n):
			bw.write(e[i].integer_representation(), self.gf_bits)
		session_key = sha256(bw.bytes()).digest()

		s = self.check_matrix * matrix.column(e)
		bw = BitWriter()
		for i in range(self.k):
			bw.write(s[i,0].integer_representation(), self.gf_bits)
		return session_key, bw.bytes()

#################### parameters #####################################

n = 3488 # block size
k = 128  # dimension
gf_bits = 12
q = 2^gf_bits # GF size

F2 = GF(2)
F2_poly.<z> = F2['z']
Fq = GF(q, names='z', modulus=z^12 + z^3 + 1)

#################### challenge ######################################

pk = KeyPair.generate(n, k, Fq)
sk, ke = pk.kem_encapsulate()
symm = ChaCha20.new(key=sk, nonce=get_random_bytes(12))
with open('../flag.txt', 'rb') as f:
	enc = symm.encrypt(f.read())

with open('flag.txt.enc', 'wb') as f:
	f.write(ke)
	f.write(symm.nonce)
	f.write(enc)

with open('public_key', 'wb') as f:
	f.write(pk.export_public())
