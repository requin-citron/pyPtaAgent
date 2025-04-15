class Net7BitInteger(object):

	@staticmethod
	def decode7bit(bytes):
		bytes = list(bytes)
		value = 0
		shift = 0
		nb_bytes = 0
		while True:
			nb_bytes += 1
			byteval = bytes.pop(0)
			if(byteval & 128) == 0: break
			value |= ((byteval & 0x7F) << shift)
			shift += 7
		return ((value | (byteval << shift)), nb_bytes)

	@staticmethod
	def encode7bit(value):
		temp = value
		bytes = ""
		while temp >= 128:
			bytes += chr(0x000000FF & (temp | 0x80))
			temp >>= 7
		bytes += chr(temp)
		return bytes
