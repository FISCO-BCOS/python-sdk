pragma solidity ^0.4.24;

contract NeedInit{
    string name;
	uint256 value;
    event onset(string newname);
    constructor(string name_,uint256 v_) public{
       name = name_;
	   value = v_;
    }

    function get() constant public returns(string,uint256){
        return (name,value);
    }

    function set(string n) public{
	emit onset(n);
    	name = n;
    }
}
