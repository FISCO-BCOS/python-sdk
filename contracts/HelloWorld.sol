pragma solidity ^0.4.24;

contract HelloWorld{
    string name;

    constructor() public{
       name = "Hello, World!";
    }

    function get(int) constant public returns(string){
        return name;
    }

    function set(string n) public{
    	name = n;
    }
}
