import React from "react";
import {render} from "react-dom";
import UserInfo from './userinfo.jsx';
import UserList from './userlist.jsx';

function get_paragraphs(element)
{
	return element
	         .contents()
	         .filter(function() { return this.nodeType == 3; })  // get text nodes
	         .map(function() { return $.trim($(this).text()); })
	         .toArray().join("\n");
}

function get_query()
{
	var query = {}
	
	location.search
		.substr(1)
		.split("&")
		.forEach(function(pair) {
			const comps = pair.split("=");
			
			if (comps.length != 2) {
				return;
			}
			
			const key   = decodeURIComponent(comps[0]);
			const value = decodeURIComponent(comps[1].replace(/\+/g, " "));
			
			query[key] = value;
		});
	
	return query;
}

const details  = document.getElementById("details_wrapper");

// landing page or error page
const nodetails = $("#details", details).empty();

const fullname = $("#fullname", details).text();
const phone    = $("#phone",    details).text();
const email    = $("#email",    details).text();
const address  = get_paragraphs($("#address", details));

const userlist  = document.getElementById("userlist");
const userlinks = $(".userlink > a", userlist);

const listdata = userlinks.map(function() {
	const url = $(this).attr("href").split("/");
	
	return {
		"username": url[url.length - 1],
		"fullname": $(this).text()
	};
}).toArray();

const query = get_query();
const needle = ("needle" in query) ? query["needle"] : null;
const truncated = $("#truncated", userlist).empty();

function setuser(username)
{
	fetch("/api/user/"  + encodeURIComponent(username))
		.then(function(response) {
			return response.json();
		}).then(function(json) {
			/*if (json["valid"] !== true || !("fullname" in json)) {
				throw new Error("Invalid response: " + json);
			}*/
			
			render(<UserInfo fullname={json.fullname} address={json.address}
			        phone={json.phone} email={json.email} />, details);
		}).catch(function(ex) {
			console.log("Couldn't get user data");
			console.log(ex);
		});
}

function search(needle)
{
	var query = "";
	
	if (needle !== null && needle !== "") {
		query = "needle=" + encodeURIComponent(needle) + "&";
	}
	
	query += "offset=0";
	
	console.log(query);
	fetch("/api/search?" + query)
		.then(function(response) {
			return response.json();
		}).then(function(json) {
			if (json["valid"] !== true || !("users" in json)) {
				throw new Error("Invalid response: " + json);
			}
			
			rjs_userlist.replace(needle, json.users, json.truncated);
		}).catch(function(ex) {
			console.log("Couldn't get user list");
			console.log(ex);
		});
}

const searchbutton = $("#search");

searchbutton.click(function() {
	const needle = $("#needle").val();
	
	search(needle);
	return false;
});

if (!nodetails) {
	render(<UserInfo fullname={fullname} address={address} phone={phone} email={email} />, details);
}

const rjs_userlist = render(<UserList userlist={listdata} needle={needle} truncated={truncated} notify={setuser} />, userlist);

