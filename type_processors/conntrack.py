from __future__ import absolute_import
# To avoid: <...>/NaCl/type_processors/conntrack.py:1: RuntimeWarning: Parent module '<...>/NaCl/type_processors' not found while handling absolute import

from NaCl import NaCl_exception, TCP, UDP, ICMP, Typed, exit_NaCl, \
    TEMPLATE_KEY_NAME

# -------------------- CONSTANTS Conntrack --------------------

TYPE_CONNTRACK 		= "conntrack"

# ---- Conntrack keys ----

CONNTRACK_KEY_LIMIT 	= "limit"
CONNTRACK_KEY_RESERVE 	= "reserve"
CONNTRACK_KEY_TIMEOUT 	= "timeout"

PREDEFINED_CONNTRACK_KEYS = [
	CONNTRACK_KEY_LIMIT,
	CONNTRACK_KEY_RESERVE,
	CONNTRACK_KEY_TIMEOUT
]

CONNTRACK_TIMEOUT_KEY_ESTABLISHED   = "established"
CONNTRACK_TIMEOUT_KEY_UNCONFIRMED   = "unconfirmed"
CONNTRACK_TIMEOUT_KEY_CONFIRMED     = "confirmed"

PREDEFINED_CONNTRACK_TIMEOUT_KEYS = [
	CONNTRACK_TIMEOUT_KEY_ESTABLISHED,
	CONNTRACK_TIMEOUT_KEY_UNCONFIRMED,
	CONNTRACK_TIMEOUT_KEY_CONFIRMED
]

PREDEFINED_CONNTRACK_TIMEOUT_INNER_KEYS = [
	TCP,
	UDP,
	ICMP
]

# -------------------- TEMPLATE KEYS (pystache) --------------------

TEMPLATE_KEY_CONNTRACKS = "conntracks"

TEMPLATE_KEY_CONNTRACK_TIMEOUTS 	= "timeouts"
TEMPLATE_KEY_CONNTRACK_TYPE 		= "type"

# -------------------- class Conntrack --------------------

class Conntrack(Typed):
	def __init__(self, nacl_state, idx, name, ctx, base_type, type_t):
		super(Conntrack, self).__init__(nacl_state, idx, name, ctx, base_type, type_t)

	def add_conntrack(self):
		timeout = self.members.get(CONNTRACK_KEY_TIMEOUT)
		timeouts = []

		if timeout is not None:
			class_name = self.get_class_name()

			if not isinstance(timeout, dict):
				exit_NaCl(self.ctx, "Invalid " + CONNTRACK_KEY_TIMEOUT + " value of " + class_name + " (needs to be an object)")

			for conntrack_type in timeout:
				t = timeout.get(conntrack_type)

				if not isinstance(t, dict):
					exit_NaCl(self.ctx, "Invalid " + conntrack_type + " value of " + class_name + " (needs to be an object)")

				tcp_timeout = t.get(TCP)
				udp_timeout = t.get(UDP)
				icmp_timeout = t.get(ICMP)

				timeouts.append({
					TEMPLATE_KEY_CONNTRACK_TYPE: conntrack_type,
					TCP: tcp_timeout,
					UDP: udp_timeout,
					ICMP: icmp_timeout
				})

		self.nacl_state.append_to_pystache_data_list(TEMPLATE_KEY_CONNTRACKS, {
			TEMPLATE_KEY_NAME: 					self.name,
			CONNTRACK_KEY_LIMIT: 				self.members.get(CONNTRACK_KEY_LIMIT),
			CONNTRACK_KEY_RESERVE: 				self.members.get(CONNTRACK_KEY_RESERVE),
			TEMPLATE_KEY_CONNTRACK_TIMEOUTS: 	timeouts
		})
        # Old:
        '''
        conntracks.append({
			TEMPLATE_KEY_NAME: 					self.name,
			CONNTRACK_KEY_LIMIT: 				self.members.get(CONNTRACK_KEY_LIMIT),
			CONNTRACK_KEY_RESERVE: 				self.members.get(CONNTRACK_KEY_RESERVE),
			TEMPLATE_KEY_CONNTRACK_TIMEOUTS: 	timeouts
		})
        '''

	# Old:
	# def validate_conntrack_key(self, key, parent_key, level, ctx):
	# New:
	# Overriding
	def validate_dictionary_key(self, key, parent_key, level, value_ctx):
		class_name = self.get_class_name()

		if level == 1:
			if key not in PREDEFINED_CONNTRACK_KEYS:
				exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key)
			return

		if parent_key == "":
			exit_NaCl(value_ctx, "Internal error: Parent key of " + key + " has not been given")

		if level == 2:
			if parent_key == CONNTRACK_KEY_TIMEOUT and key not in PREDEFINED_CONNTRACK_TIMEOUT_KEYS:
				exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key + " in " + self.name + "." + parent_key)
		elif level == 3:
			if parent_key not in PREDEFINED_CONNTRACK_TIMEOUT_KEYS:
				exit_NaCl(value_ctx, "Internal error: Invalid parent key " + parent_key + " of " + key)
			if key not in PREDEFINED_CONNTRACK_TIMEOUT_INNER_KEYS:
				exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key)
		else:
			exit_NaCl(value_ctx, "Invalid " + class_name + " member " + key)

	# Old:
	# def resolve_conntrack_value(self, dictionary, key, value):
	# New:
	# Overriding
	def resolve_dictionary_value(self, dictionary, key, value):
		# Add found value
		dictionary[key] = self.nacl_state.resolve_value(value)

	# Overriding
	# def validate_and_resolve_dictionary_val(self, dictionary, level_key, parent_key, level, value):
	#    self.validate_conntrack_key(level_key, parent_key, level, value)
	#    self.resolve_conntrack_value(dictionary, level_key, value)

	# Main processing method
	def process(self):
		if self.res is None:
			# Then process

			self.process_ctx()
			self.process_assignments()
			self.add_conntrack()

			self.res = self.members
			# Or:
			# self.res = resolve_value(LANGUAGE, ...)

		return self.res

# < class Conntrack

def create_connstrack_pystache_lists(nacl_state):
	nacl_state.create_pystache_data_lists([
        TEMPLATE_KEY_CONNTRACKS
	])

# TODO: Set only allowed to create ONE Conntrack object per NaCl

def init(nacl_state):
    print "Init conntrack: Conntrack"

    nacl_state.add_type_processor(TYPE_CONNTRACK, Conntrack, True)

    create_connstrack_pystache_lists(nacl_state)
