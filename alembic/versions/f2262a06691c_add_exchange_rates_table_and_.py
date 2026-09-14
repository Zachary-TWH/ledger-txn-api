def unsign_int_to_bits(x):
    if x == 0:
        return "0"
    else:
        res = ''
        while x > 0:
            if x % 2 == 0:
              res =  "0" + res # res+ "0" 
            else:
              res =  "1" + res #res+ "1"
            x = (x//2)
        return res


def add_one_bits(x):

  if x[-1] == "0":
    return x[0:len(x)-1] + "1"

  z = ""
  carrier = 1
  for t in x[::-1]:
    if carrier+int(t) == 2: 
      z = "0" + z
      carrier = 1
    elif carrier+int(t) == 1: 
      z = "1" + z
      carrier = 0
    else:
      z = "0" + z
      carrier = 0

  return (z)

# You may add any helper function you need

def sign_int_to_bits(x):
    if x >= 0:
        return '0' + int_to_bits(x)
    else:
        temp = int_to_bits(-x)
        temp = flip_bits(temp)
        temp = int_to_bits(int(temp, 2))
        if temp[0] == '0':
            temp = '1' + temp
        return temp

def sign_extend(x, n):
    z = x[0]
    if n <= len(x) or len(x)==0:  # invalid input
        return x
    else:
        return (n - len(x))*z + x

def unsign_extend(x, n):
    if n <= len(x) or len(x)==0:  # invalid input
        return x
    else:
        return (n - len(x))*"0" + x

def bits_to_hex(x):
    if len(x) % 4 != 0:
        return ''
    else:
        res = ''
        for i in range(0,len(x),4): #convert 4 bits each step
          if x[i:i+4] == '0000':
              res = res + '0'
          elif x[i:i+4] == '0001':
              res = res + '1'
          elif x[i:i+4] == '0010':
              res = res + '2'
          elif x[i:i+4] == '0011':
              res = res + '3'
          elif x[i:i+4] == '0100':
              res = res + '4'
          elif x[i:i+4] == '0101':
              res = res + '5'
          elif x[i:i+4] == '0110':
              res = res + '6'
          elif x[i:i+4] == '0111':
              res = res + '7'
          elif x[i:i+4] == '1000':
              res = res + '8'
          elif x[i:i+4] == '1001':
              res = res + '9'
          elif x[i:i+4] == '1010':
              res = res + 'A'
          elif x[i:i+4] == '1011':
              res = res + 'B'
          elif x[i:i+4] == '1100':
              res = res + 'C'
          elif x[i:i+4] == '1101':
              res = res + 'D'
          elif x[i:i+4] == '1110':
              res = res + 'E'
          elif x[i:i+4] == '1111':
              res = res + 'F'
    return res



def fraction_to_bits(x, n):
    res = ''
    for i in range(n):
        x = x * 2                  
        res = res + str(int(x))    
        x = x - int(x)             
    if x >= 0.5:
        res = bin(int(res, 2) + 1)[2:].zfill(len(res))
    return res

def text_to_bit_string(text):
    encoded = text.encode("utf-8")
    
    binary = ""
    
    for byte in encoded:
        binary += f"{byte:08b}"
    
    return binary

base64 = {
    '000000': 'A', '000001': 'B', '000010': 'C', '000011': 'D',
    '000100': 'E', '000101': 'F', '000110': 'G', '000111': 'H',
    '001000': 'I', '001001': 'J', '001010': 'K', '001011': 'L',
    '001100': 'M', '001101': 'N', '001110': 'O', '001111': 'P',
    '010000': 'Q', '010001': 'R', '010010': 'S', '010011': 'T',
    '010100': 'U', '010101': 'V', '010110': 'W', '010111': 'X',
    '011000': 'Y', '011001': 'Z', '011010': 'a', '011011': 'b',
    '011100': 'c', '011101': 'd', '011110': 'e', '011111': 'f',
    '100000': 'g', '100001': 'h', '100010': 'i', '100011': 'j',
    '100100': 'k', '100101': 'l', '100110': 'm', '100111': 'n',
    '101000': 'o', '101001': 'p', '101010': 'q', '101011': 'r',
    '101100': 's', '101101': 't', '101110': 'u', '101111': 'v',
    '110000': 'w', '110001': 'x', '110010': 'y', '110011': 'z',
    '110100': '0', '110101': '1', '110110': '2', '110111': '3',
    '111000': '4', '111001': '5', '111010': '6', '111011': '7',
    '111100': '8', '111101': '9', '111110': '+', '111111': '/'
}


def bit_string_to_base64(bit_str): 
    new = ""
    if len(bit_str) % 6 !=0:
      bit_str = bit_str + (6- len(bit_str) % 6 )*"0"

    for x in range(0,len(bit_str),6):
      if bit_str[x:x+6] in base64:
        print(bit_str[x:x+6])
        new = new + base64[bit_str[x:x+6]]

    if len(new) < 4:
      new = new + (4-len(new))*"="
    
    return(new)
