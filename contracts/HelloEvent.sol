pragma solidity ^0.4.24;

contract HelloEvent{
    string name;
    event onset(string newname);
	event on_number(string name,int indexed age);
	event on_two_event(string name ,int indexed age, string indexed key);
	event on_address(address addr);
    constructor() public{
       name = "Hello, Event!";
    }

    function get() constant public returns(string){
        return name;
    }
	
	function settwo(string n ,int i,string key) public
	{
		emit on_two_event(name,i,key);
		name = n;
		
	}
	
	function setnum(string n ,int i) public
	{
		emit on_number(name,i);
		name = n;
	}

    function set(string n) public{
		emit onset(n);
		emit on_number(n,5);
		emit on_address(0xAb3BB3C6111ff74A280B3A560eB204FC9538061E);
		name = n;
		
    }
}
