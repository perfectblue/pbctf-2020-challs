from Crypto.Util.number import getRandomInteger, getRandomRange
from Crypto.Random import get_random_bytes
from Crypto.Cipher import ChaCha20
from hashlib import sha256
import io
from sage.matrix.berlekamp_massey import berlekamp_massey

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

class BitReader:
	def __init__(self, file):
		self.file = file
		self.buffer = 0
		self.buffer_len = 0

	def read(self, n):
		while self.buffer_len < n:
			m = self.file.read(1)
			if len(m) == 0:
				raise EOFError()
			self.buffer += m[0]<<self.buffer_len
			self.buffer_len += 8
		x = self.buffer&((1<<n)-1)
		self.buffer >>= n
		self.buffer_len -= n
		return x

#################### public key system ##############################

class Code:
	def __init__(self, n, k, field, a=None, z=None):
		self.n = n
		self.k = k
		self.field = field
		self.poly_ring = field['x']
		nz = list(self.field)
		nz.remove(self.field(0))
		self.a = a or random_subset(nz, self.n)
		self.z = z or [ random_choice(nz) for _ in range(n) ]

	def check_matrix(self):
		h = matrix.zero(self.field, self.k, self.n)
		for i in range(self.k):
			for j in range(self.n):
				h[i, j] = self.z[j] * self.a[j]^i
		return h

	def decode(self, s):
		locator = berlekamp_massey(list(reversed(s)))
		print('roots:', locator.degree())
		assert locator.is_monic()
		R.<x> = self.field['x']
		valuator = R(s) * locator % (x^self.k)
		assert valuator.degree() <= locator.degree()-1
		locator_deriv = locator.derivative()

		e = [self.field(0)]*self.n
		for root, _ in locator.roots():
			aj = root^-1
			loc = self.a.index(aj)
			d = locator_deriv(root) * -root
			val = valuator(root) / d / self.z[loc]
			e[loc] = val
		return e

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
		for i in range(self.k):
			for j in range(self.n):
				bw.write(self.check_matrix[i,j].integer_representation(), self.gf_bits)
		return bw.bytes()

	def import_public(self, src):
		br = BitReader(src)
		h = matrix.zero(self.field, self.k, self.n)
		for i in range(self.k):
			for j in range(self.n):
				h[i, j] = self.field.fetch_int(br.read(self.gf_bits))
		self.check_matrix = h

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

	def kem_decapsulate(self, kem):
		s = []
		br = BitReader(io.BytesIO(kem))
		for _ in range(self.k):
			s.append(self.field.fetch_int(br.read(self.gf_bits)))

		s = matrix.column(s)
		s = self.obfuscator * s

		e = self.code.decode([s[i,0] for i in range(self.k)])
		bw = BitWriter()
		for i in range(self.n):
			bw.write(e[i].integer_representation(), self.gf_bits)
		session_key = sha256(bw.bytes()).digest()
		return session_key

	def sidelnikov_shestakov_attack(self):
		def nz_sol(m):
			k = m.transpose().kernel()
			while True:
				sol = k.random_element()
				if sol != 0:
					return sol

		def fit_geom(av):
			z = av[0]
			if z == 0:
				raise ValueError('not geometric series')
			a = av[1]/av[0]
			for i in range(2, len(av)):
				if z*a^i != av[i]:
					raise ValueError('not geometric series')
			return a, z

		n = self.n
		k = self.k
		Fq = self.field

		short_sol = nz_sol(self.check_matrix[:,:k+1])
		M = self.check_matrix.echelon_form()
		assert M[:,:k+1]*short_sol == 0

		for a_kp1 in Fq:
			# assume a[0] = 0
			# assume a[k] = 1
			# assume a[k+1] = a_kp1
			if a_kp1 == 0 or a_kp1 == 1: # both already taken
				continue
			a = [Fq(0)]
			try:
				for i in range(1, k):
					m = Matrix([
						[ 1, M[0,k]/M[i,k]           ],
						[ 1, M[0,k+1]/M[i,k+1]*a_kp1 ],
					])
					rhs = matrix.column([1, a_kp1], ring=Fq)
					sol = m.solve_right(rhs)
					a.append(sol[0,0])
				a.append(Fq(1))
				a.append(a_kp1)
			except ValueError: # no solution to the linear system
				continue
			print('a_kp1', a_kp1)
			#print('a[]', a)
			G_left = matrix.zero(Fq, k, k+1)
			for i in range(k):
				for j in range(k+1):
					G_left[i,j] = short_sol[j] * a[j]^i
			c_vec = nz_sol(G_left)
			#print('c_vec[]', c_vec)

			G_left = matrix.zero(Fq, k, k+1)
			for i in range(k):
				for j in range(k+1):
					G_left[i,j] = c_vec[j] * a[j]^i

			if G_left * short_sol != 0:
				continue

			#print('G_left:')
			#print(G_left)
			H_inv = G_left[:,:k] / self.check_matrix[:,:k]
			G = H_inv * self.check_matrix
			#print('G_recov:')
			#print(G)

			av = []
			zv = []
			for j in range(n):
				try:
					a, z = fit_geom([G[i,j] for i in range(k)])
					av.append(a)
					zv.append(z)
				except ValueError:
					break
			if len(av) != n:
				continue
			self.obfuscator = H_inv
			self.code = Code(n, k, Fq, av, zv)
			return av, zv, H_inv

#################### parameters #####################################

n = 3488 # block size
k = 128  # dimension
gf_bits = 12
q = 2^gf_bits # GF size

F2 = GF(2)
F2_poly.<z> = F2['z']
Fq = GF(q, names='z', modulus=z^12 + z^3 + 1)
R.<x> = Fq['x']

if False:
	key = KeyPair.generate(n, k, Fq)
	sk, kem = key.kem_encapsulate()
	sk_recov = key.kem_decapsulate(kem)
	assert sk == sk_recov

key = KeyPair(n, k, Fq)
with open('dist/public_key', 'rb') as f:
	key.import_public(f)
key.sidelnikov_shestakov_attack()

with open('dist/flag.txt.enc', 'rb') as f:
	kem_data = f.read(k*gf_bits//8)
	nonce = f.read(12)
	ctext = f.read()
sk = key.kem_decapsulate(kem_data)
print('sk:', sk.hex())
symm = ChaCha20.new(key=sk, nonce=nonce)
print(symm.decrypt(ctext))
