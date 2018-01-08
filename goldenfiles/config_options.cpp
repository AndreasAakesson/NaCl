// This file is a part of the IncludeOS unikernel - www.includeos.org
//
// Copyright 2017 IncludeOS AS, Oslo, Norway
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// Autogenerated by NaCl

#include <iostream>
#include <net/inet4>
#include <net/super_stack.hpp>
#include <net/ip4/cidr.hpp>
#include <plugins/nacl.hpp>
#include <syslogd>

using namespace net;

std::shared_ptr<Conntrack> nacl_ct_obj;

namespace custom_made_classes_from_nacl {

class My_Filter : public nacl::Filter {
public:
	Filter_verdict<IP4> operator()(IP4::IP_packet_ptr pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return {nullptr, Filter_verdict_type::DROP};
}
if (pckt->ip_protocol() == Protocol::ICMPv4) {
auto icmp_pckt = icmp4::Packet(std::move(pckt));

if ((icmp_pckt.ip().ip_src() == IP4::addr{10,0,0,1} or icmp_pckt.ip().ip_src() == IP4::addr{10,0,0,2} or (icmp_pckt.ip().ip_src() >= IP4::addr{130,10,20,10} and icmp_pckt.ip().ip_src() <= IP4::addr{130,10,20,30}) or ip4::Cidr{140,0,0,0,24}.contains(icmp_pckt.ip().ip_src()))) {
if (icmp_pckt.type() == icmp4::Type::ECHO) {
return {icmp_pckt.release(), Filter_verdict_type::ACCEPT};
}
if (icmp_pckt.type() == icmp4::Type::DEST_UNREACHABLE) {
return {nullptr, Filter_verdict_type::DROP};
}
}
pckt = icmp_pckt.release();
}
if (pckt->ip_protocol() == Protocol::TCP) {
auto& tcp_pckt = static_cast<tcp::Packet&>(*pckt);

if ((tcp_pckt.src_port() == 10 or tcp_pckt.src_port() == 20 or tcp_pckt.src_port() == 30 or (tcp_pckt.src_port() >= 40 and tcp_pckt.src_port() <= 50) or tcp_pckt.src_port() == 60)) {
return {nullptr, Filter_verdict_type::DROP};
}
if (tcp_pckt.dst_port() == 80) {
if ((tcp_pckt.ip_src() == IP4::addr{10,0,0,1} or tcp_pckt.ip_src() == IP4::addr{10,0,0,2} or (tcp_pckt.ip_src() >= IP4::addr{130,10,20,10} and tcp_pckt.ip_src() <= IP4::addr{130,10,20,30}) or ip4::Cidr{140,0,0,0,24}.contains(tcp_pckt.ip_src()))) {
return {std::move(pckt), Filter_verdict_type::ACCEPT};
}
}
if (tcp_pckt.dst_port() == 40) {
return {nullptr, Filter_verdict_type::DROP};
}
}
return {nullptr, Filter_verdict_type::DROP};

	}
};

} //< namespace custom_made_classes_from_nacl

void register_plugin_nacl() {
	INFO("NaCl", "Registering NaCl plugin");

	auto& s = Super_stack::get<IP4>(3);
	s.negotiate_dhcp(10.0, [&s] (bool timedout) {
		if (timedout) {
			INFO("NaCl plugin interface s", "DHCP timeout (%s) - falling back to static configuration", s.ifname().c_str());
			s.network_config(IP4::addr{10,0,0,60}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1});
		}
	});
	auto& something_else = Super_stack::get<IP4>(2);
	something_else.negotiate_dhcp(10.0, [&something_else] (bool timedout) {
		if (timedout) {
			INFO("NaCl plugin interface something_else", "DHCP request timed out. Nothing to do.");
			return;
		}
		INFO("NaCl plugin interface something_else", "IP address updated: %s", something_else.ip_addr().str().c_str());
	});
	auto& something = Super_stack::get<IP4>(1);
	something.negotiate_dhcp(10.0, [&something] (bool timedout) {
		if (timedout) {
			INFO("NaCl plugin interface something", "DHCP request timed out. Nothing to do.");
			return;
		}
		INFO("NaCl plugin interface something", "IP address updated: %s", something.ip_addr().str().c_str());
	});
	auto& some_other = Super_stack::get<IP4>(0);
	some_other.negotiate_dhcp(10.0, [&some_other] (bool timedout) {
		if (timedout) {
			INFO("NaCl plugin interface some_other", "DHCP timeout (%s) - falling back to static configuration", some_other.ifname().c_str());
			some_other.network_config(IP4::addr{10,0,0,50}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1});
		}
	});
	auto& eth0 = Super_stack::get<IP4>(4);
	eth0.network_config(IP4::addr{10,0,0,42}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1}, IP4::addr{8,8,8,8});

	custom_made_classes_from_nacl::My_Filter my_filter;

	eth0.ip_obj().input_chain().chain.push_back(my_filter);

	// Ct

	nacl_ct_obj = std::make_shared<Conntrack>();

	INFO("NaCl", "Enabling Conntrack on eth0");
	eth0.enable_conntrack(nacl_ct_obj);
}
