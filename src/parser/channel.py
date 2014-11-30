class Channel:

	def __init__(self):
		pass

	def init(self):
		queue = []

	def actions(self):
		ret = {}
		def send_prec(fr,m):
			return False
		def send_eff(fr,m):
			queue.append(m)
		def send_output(fr,m):
			return None
		d = { "arityprec": 2, "atype": "input", "prec": send_prec, "arityoutput": 2, "output": send_output, "fullname": "send(m)", "arityeff": 2, "eff": send_eff, }
		ret["send"] = d
		def receive_prec(to,m):
			return len(queue) > 0
		def receive_eff(to,m):
			queue = queue[1:]
		def receive_output(to,m):
			m = queue[0]
		d = { "arityprec": 2, "atype": "output", "prec": receive_prec, "arityoutput": 2, "output": receive_output, "fullname": "receive(m)", "arityeff": 2, "eff": receive_eff, }
		ret["receive"] = d
		return ret

	def tasks(self):
		return [ "receive" ]


allclasses =  { "Channel" : Channel }
