pragma solidity ^0.6.3;
pragma experimental ABIEncoderV2;

contract TestStruct {

      struct User {
        string name;
        uint256 age;
     }
	 
	 event onadd(string newname);
	 event onadduser(string newname,User u);
	 event onaddusers(uint256 len,User[] u);

    mapping (string => User) users;
	
	  constructor() public
    {
		User memory u = User("alice",25);
		addUser(u);
    }
    
    
     function addUser (User memory _user) public {

           addbyname(_user.name,_user);

        
    }
	
	function addbyname (string memory name,User memory _user) public {

       users[name] = _user;
		emit onadd(name);
		emit onadduser(name,_user);
        
    }

    function addUsers (User [] memory _users) public {

        for (uint i = 0; i < _users.length; i++) {
           //users[_users[i].name] = _users[i];
			addUser(_users[i]);
        }
		emit onaddusers(_users.length,_users);
    }

    function getUser (string memory username) public view returns (User memory) {

        //bytes32 hash = keccak256(abi.encode(username));
        return users[username];
    }
    event on_putbytes(string n,bytes32 b);
    function putbytes(string memory uname,bytes32 br) public
    {
        emit on_putbytes(uname,br);
    }
}