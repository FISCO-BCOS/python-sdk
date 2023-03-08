pragma solidity>=0.4.24 <0.6.11;
pragma experimental ABIEncoderV2;


contract ArrayDemo{
    event on_set(uint256  value,string[]  data);
	uint256 value;
	string[] data;
	
	constructor() public {
		value = 0;
    }
	
    function total() public view returns (uint256) {
        return data.length;
    }

	function get(uint256 index)public view returns (uint256,string) {
		return (value,data[index]);
	}
	

    function add(uint256  v,string[]  inputdata) public returns (uint256) {
	
		value = v;
	     for(uint i=0; i<inputdata.length; ++i) {
            data.push(inputdata[i]);
		}
		emit on_set(value,data);
		return data.length;
    }
}
