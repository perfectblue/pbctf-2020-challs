pragma solidity 0.4.24;

contract pbcoin{
    
    address public owner;
    string private lammer;
    bytes private gol;
    string private seed;                     //rodl should be the seed. Players will brute it if chall not on blockchain
    bytes private seed_in;
    
    /* Only Contract Creator will be the owner */
    function pbcoin() public payable {
        owner = msg.sender;
    }
    
    /* Only owner can set seed, as EVM isn't deployed, we want players to brute it */
    function setseed(string _seed) public{
        require(msg.sender == owner);
        seed = _seed;
        seed_in = bytes(seed);
    }
    
    
    function getseed() constant public returns(string){
        return seed;
    }

    
    /* Encryption Routine */
    function coinosama(string text) constant public returns(string) {
        uint256 snum = 72;
        require(block.number == snum);      // Running this will not ofcourse let you test it locally lol. Comment it out if you are testing locally for challenge debug purpose
        uint256 blk_num = snum;
        string memory hxhx;
        uint256[] memory arr = new uint[](10);
        assembly {
            mstore(add(arr, 32), 39) 
            mstore(add(arr, 64), 13)
            mstore(add(arr, 96), 93)
            mstore(add(arr, 128), 45)
            mstore(add(arr, 160), 59)
            mstore(add(arr, 192), 68)
            mstore(add(arr, 224), 77)
            mstore(add(arr, 256), 5)
            mstore(add(arr, 288), 2)
            mstore(add(arr, 320), 7)
        }
        
        // [39,13,93,45,59,68,77,5,2,7]
        
       // string storage rotenc = this.rot7Enc(text);
        hxhx = this.vegotosan(text);
        gol = bytes(hxhx);
        
        for (uint i=0; i<gol.length; i++){
            gol[i] = (gol[i]^bytes1(arr[(i+5)%10]))^bytes1(block.number); // should be replaced by blk_num
        }
        
        
         require(seed_in.length == 4);
         require(this.gokusan(bytes(seed), "pbctf{not_the_flag}") == 0x660250a58689ff6ec3acb5efeb01d0ea67599efd2482c1761d5fb81c8b7b5976);
        
        /*
        gol = this.customEnc(gol);
        
        lammer = string(gol);
        */
        
        
         if(gol.length > 6){                            // Players will see that real flag should be > 6 obviously
            uint offset = gol.length - 2;                  // Total length - 2
            gol[offset-8] = (seed_in[2] ^ gol[offset-8]) ^ seed_in[3] ^ gol[offset-4];
            gol[offset-2] = (seed_in[0] ^ gol[offset-2]) ^ seed_in[1] ^ gol[offset-6];
        }
        else{
            assembly{
                jump(0x38)
            }
        } 
        
        
        return string(gol);
        
    }


    function freeflagforyounoob() constant public returns(bytes32){
        bytes32 _bytes = "pbctf{obviously_not_the_flag}";
        return _bytes;
    }
    
   function vegotosan(string text) view public returns(string) {
        uint256 length = bytes(text).length;
        for (var i = 0; i < length; i++) {
            byte char = bytes(text)[i];
            //inline assembly to modify the string
            assembly {
                char := byte(0,char) // get the first byte
                if and(gt(char,0x73), lt(char,0x7B)) // if the character is in [n,z], i.e. wrapping. 
                { char:= sub(0x60, sub(0x7A,char)) } // subtract from the ascii number a by the difference char is from z. 
                if iszero(eq(char, 0x20)) // ignore spaces
                {mstore8(add(add(text,0x20), mul(i,1)), add(char,7))} // add 7 to char. 
            }
        }
        return text;
    }

/* SHA-256 Hashing with HMAC */
function gokusan(bytes memory duper, bytes memory chaiyan) public pure returns (bytes32) {
    bytes32 keyl;
    bytes32 keyr;
    uint i;
    if (duper.length > 64) {
        keyl = sha256(duper);
    } else {
        for (i = 0; i < duper.length && i < 32; i++)
            keyl |= bytes32(uint(duper[i]) * 2 ** (8 * (31 - i)));
        for (i = 32; i < duper.length && i < 64; i++)
            keyr |= bytes32(uint(duper[i]) * 2 ** (8 * (63 - i)));
    }
    bytes32 threesix = 0x3636363636363636363636363636363636363636363636363636363636363636;
    bytes32 fivec = 0x5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c;
    return sha256(fivec ^ keyl, fivec ^ keyr, sha256(threesix ^ keyl, threesix ^ keyr, chaiyan));
}
 
    
    /* Decryption Routine */
    function Decrypt(string text) constant public returns(bytes32){
        bytes32 _bytes = "Was very bored to implement this";
        return _bytes;
    }
    
    /* SHA1 useless to increase bytecode size and noise */
    function krilliansan(bytes krillz) public constant returns(bytes20 ret){
        assembly {
            switch div(calldataload(0), exp(2, 224))
            case 0x1605782b { }
            default { revert(0, 0) }
            let data := add(calldataload(4), 4)

            // Get the data length, and point data at the first byte
            let len := calldataload(data)
            data := add(data, 32)

            // Find the length after padding
            let totallen := add(and(add(len, 1), 0xFFFFFFFFFFFFFFC0), 64)
            switch lt(sub(totallen, len), 9)
            case 1 { totallen := add(totallen, 64) }

            let h := 0x6745230100EFCDAB890098BADCFE001032547600C3D2E1F0

            for { let i := 0 } lt(i, totallen) { i := add(i, 64) } {
                // Load 64 bytes of data
                calldatacopy(0, add(data, i), 64)

                // If we loaded the last byte, store the terminator byte
                switch lt(sub(len, i), 64)
                case 1 { mstore8(sub(len, i), 0x80) }

                // If this is the last block, store the length
                switch eq(i, sub(totallen, 64))
                case 1 { mstore(32, or(mload(32), mul(len, 8))) }

                // Expand the 16 32-bit words into 80
                for { let j := 64 } lt(j, 128) { j := add(j, 12) } {
                    let temp := xor(xor(mload(sub(j, 12)), mload(sub(j, 32))), xor(mload(sub(j, 56)), mload(sub(j, 64))))
                    temp := or(and(mul(temp, 2), 0xFFFFFFFEFFFFFFFEFFFFFFFEFFFFFFFEFFFFFFFEFFFFFFFEFFFFFFFEFFFFFFFE), and(div(temp, exp(2, 31)), 0x0000000100000001000000010000000100000001000000010000000100000001))
                    mstore(j, temp)
                }
                for { let j := 128 } lt(j, 320) { j := add(j, 24) } {
                    let temp := xor(xor(mload(sub(j, 24)), mload(sub(j, 64))), xor(mload(sub(j, 112)), mload(sub(j, 128))))
                    temp := or(and(mul(temp, 4), 0xFFFFFFFCFFFFFFFCFFFFFFFCFFFFFFFCFFFFFFFCFFFFFFFCFFFFFFFCFFFFFFFC), and(div(temp, exp(2, 30)), 0x0000000300000003000000030000000300000003000000030000000300000003))
                    mstore(j, temp)
                }

                let x := h
                let f := 0
                let k := 0
                for { let j := 0 } lt(j, 80) { j := add(j, 1) } {
                    switch div(j, 20)
                    case 0 {
                        // f = d xor (b and (c xor d))
                        f := xor(div(x, exp(2, 80)), div(x, exp(2, 40)))
                        f := and(div(x, exp(2, 120)), f)
                        f := xor(div(x, exp(2, 40)), f)
                        k := 0x5A827999
                    }
                    case 1{
                        // f = b xor c xor d
                        f := xor(div(x, exp(2, 120)), div(x, exp(2, 80)))
                        f := xor(div(x, exp(2, 40)), f)
                        k := 0x6ED9EBA1
                    }
                    case 2 {
                        // f = (b and c) or (d and (b or c))
                        f := or(div(x, exp(2, 120)), div(x, exp(2, 80)))
                        f := and(div(x, exp(2, 40)), f)
                        f := or(and(div(x, exp(2, 120)), div(x, exp(2, 80))), f)
                        k := 0x8F1BBCDC
                    }
                    case 3 {
                        // f = b xor c xor d
                        f := xor(div(x, exp(2, 120)), div(x, exp(2, 80)))
                        f := xor(div(x, exp(2, 40)), f)
                        k := 0xCA62C1D6
                    }
                    // temp = (a leftrotate 5) + f + e + k + w[i]
                    let temp := and(div(x, exp(2, 187)), 0x1F)
                    temp := or(and(div(x, exp(2, 155)), 0xFFFFFFE0), temp)
                    temp := add(f, temp)
                    temp := add(and(x, 0xFFFFFFFF), temp)
                    temp := add(k, temp)
                    temp := add(div(mload(mul(j, 4)), exp(2, 224)), temp)
                    x := or(div(x, exp(2, 40)), mul(temp, exp(2, 160)))
                    x := or(and(x, 0xFFFFFFFF00FFFFFFFF000000000000FFFFFFFF00FFFFFFFF), mul(or(and(div(x, exp(2, 50)), 0xC0000000), and(div(x, exp(2, 82)), 0x3FFFFFFF)), exp(2, 80)))
                }

                h := and(add(h, x), 0xFFFFFFFF00FFFFFFFF00FFFFFFFF00FFFFFFFF00FFFFFFFF)
            }
            h := or(or(or(or(and(div(h, exp(2, 32)), 0xFFFFFFFF00000000000000000000000000000000), and(div(h, exp(2, 24)), 0xFFFFFFFF000000000000000000000000)), and(div(h, exp(2, 16)), 0xFFFFFFFF0000000000000000)), and(div(h, exp(2, 8)), 0xFFFFFFFF00000000)), and(h, 0xFFFFFFFF))
            //log1(0, 0, h)
            mstore(0, h)
            return(12, 20)
        }
    }
    
    
    /* Helpers necessary for SHA-1 */
    function stringToBytes(string memory source) returns (bytes result) {
    assembly {
        result := mload(add(source, 32))
    }
}

  function bytes20ToString(bytes20 x) constant returns (string) {
    bytes memory bytesString = new bytes(20);
    uint charCount = 0;
    for (uint j = 0; j < 20; j++) {
        byte char = byte(bytes32(uint(x) * 2 ** (8 * j)));
        if (char != 0) {
            bytesString[charCount] = char;
            charCount++;
        }
    }
    bytes memory bytesStringTrimmed = new bytes(charCount);
    for (j = 0; j < charCount; j++) {
        bytesStringTrimmed[j] = bytesString[j];
    }
    return string(bytesStringTrimmed);
} 
    
}
