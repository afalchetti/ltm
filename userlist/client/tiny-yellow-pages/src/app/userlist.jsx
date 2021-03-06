import React from "react";
import "whatwg-fetch";

class UserList extends React.Component
{
	constructor(props)
	{
		super(props);
		
		const userlist  = ("userlist"  in props) ? props.userlist  : [];
		const needle    = ("needle"    in props) ? props.needle    : null;
		const truncated = ("truncated" in props) ? props.truncated : false;
		
		this.state = {
			userlist: userlist,
			needle: needle,
			listsize: userlist.length,
			truncated: truncated
		};
		
		this.append     = this.append.bind(this);
		this.replace    = this.replace.bind(this);
		this.loadmore   = this.loadmore.bind(this);
		this.notifyinfo = this.notifyinfo.bind(this);
		
		this.notifyexternal = ("notify" in props) ? props.notify : function(x) {};
	}
	
	append(userlist, truncated)
	{
		const newlist = this.state.userlist.concat(userlist);
		this.setState({
			truncated: truncated,
			userlist: newlist,
			listsize: newlist.length
		});
	}
	
	replace(newneedle, userlist, truncated)
	{
		this.setState({
			needle: newneedle,
			truncated: truncated,
			userlist: userlist,
			listsize: userlist.length
		});
	}
	
	loadmore()
	{
		const ulist = this;
		var query = "";
		
		if (this.state.needle !== null && this.state.needle !== "") {
			query = "needle=" + encodeURIComponent(this.state.needle) + "&";
		}
		
		query += "offset=" + encodeURIComponent(this.state.listsize);
		
		fetch("/api/search?" + query, {credentials: "same-origin"})
			.then(function(response) {
				return response.json();
				
			}).then(function(json) {
				if (json["valid"] !== true || !("users" in json)) {
					throw new Error("Invalid response: " + json);
				}
				
				ulist.append(json["users"], json["truncated"]);
				
			}).catch(function(ex) {
				console.log("Couldn't get extra user list");
				console.log(ex);
			});
	}
	
	notifyinfo(username)
	{
		this.notifyexternal(username);
	}
	
	render()
	{
		const namelist = this.state.userlist.map(user => (
		                 <li key={user.username}>
		                 <a onClick={() => this.notifyinfo(user.username)}>
		                     {user.fullname}
		                 </a>
		                 </li>
		                 ));
		
		if (this.state.truncated) {
			return (
			<ul id="userlist">
				{namelist}
				<li>
				<a onClick={this.loadmore} id="truncated">Load more...</a>
				</li>
			</ul>
			);
		}
		else {
			return <ul id="userlist">{namelist}</ul>;
		}
	}
}

export default UserList;
