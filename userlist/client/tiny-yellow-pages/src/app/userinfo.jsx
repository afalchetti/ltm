import React from "react";

class UserInfo extends React.Component
{
	constructor(props)
	{
		super(props);
	}
	
	render()
	{
		const address = this.props.address.replace("\n", "<br/>");
		
		return (
		<div id="details">
			<h2>{this.props.fullname}</h2>
			<div className="infotable">
				<div className="infoentry">
					<p>Address:</p>
					<p dangerouslySetInnerHTML={{__html: address}}></p>
				</div>
				<div className="infoentry">
					<p>Phone Number:</p>
					<p>{this.props.phone}</p>
				</div>
				<div className="infoentry">
					<p>E-mail:</p>
					<p>{this.props.email}</p>
				</div>
			</div>
		</div>
		);
	}
}

export default UserInfo;
