pragma solidity>=0.4.24 <0.6.11;

contract LiteNote{
    
    struct Note{
        string timestamp;
        string title;
        string content;
    }
  
    Note[] noteList;
    bool isPublic;
    address owner;
    event on_write(address  writer,string timestamp,string title,uint256 index);
    event on_set_owner(address oldOwner,address newOwner);
    event on_set_public(bool oldState,bool newState);
    constructor() public {
	owner = tx.origin;
	isPublic = false;

    }

    function get_owner() public view returns (address)
    {
		return owner;
	}
    

    function ispublic() public view returns (bool)
    {
        return isPublic;
    }

    function setpublic(bool isPublic_) public returns (bool)
    {
	   if(owner != address(0x0) )
       {
             require(tx.origin==owner,"only owner can change isPublic");
       }
	   bool oldstate = isPublic;
       isPublic  = isPublic_;
	   emit on_set_public(oldstate,isPublic);
       return isPublic;
    }

    function set_owner(address  newOwner) public returns (address)
    {
       if(owner != address(0x0) )
       {
            require(tx.origin == owner,"only owner can change new owner");
        }
	    
      address oldOwner = owner;
      owner = newOwner;
      emit on_set_owner(oldOwner,newOwner); 
      return oldOwner;

    }

    function total() public view returns (uint256) {
        return noteList.length;
    }

    function read(uint256 index) public view returns (string memory,string memory,string memory)
    {
	 if (index>=noteList.length)
		return ("","","");
         Note memory n = noteList[index];
	 return (n.timestamp,n.title,n.content);
    }

    function write(string memory timestamp,string memory title,string memory content) public returns (uint256) {
	if(isPublic == false)
	{
	    require(tx.origin == owner,"only owner can add note");	
	}
	uint256 currIndex = noteList.length;
	Note memory n = Note(timestamp,title,content);
	noteList.push(n);
	emit on_write(owner,timestamp,title,currIndex);
	return noteList.length;
    }
}
