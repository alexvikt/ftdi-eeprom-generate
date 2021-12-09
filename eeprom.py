
eeprom_name = 'eeprom.bin'

ua = [0]*128
n = 0
for i in 'User area':
    ua[n] = ord(i)
    n+=1
va = 'Vendor area'
pa = 'Product area'
sa = 'Serial area'

# import user
# va = user.va()
# pa = user.pa()
# sa = user.sa()
# ua = user.ua()

# For 2232
# ch_0 - PortA; ch_2 - PortB
# D2xx
#       RS232   -       0x0
#       245 fifo -      0x1
#       cpu fifo -      0x2
#       opto isolate -  0x4
# Virtual COM Port
#       RS232   -       0x8
#       245 fifo -      0x9
#       cpu fifo -      0xa
#       opto isolate -  0xc
#
# For 4232
# ch_0 - PortA; ch_2 - PortB; ch_1 - PortC; ch_3 - PortD
# Virtual COM Port -    0x8
# D2xx Direct   -       0x0
#


ch_0=1
ch_1=0
ch_2=8
ch_3=0

idVendor='0403'
idProduct='6010'

#
# 0x0002 - TYPE_BM
# 0x0004 - TYPE_AM
# 0x0005 - FT2232C
# 0x0006 - TYPE_R
# 0x0007 - FT2232H
# 0x0008 - FT4232H
# 0x0009 - FT232H
#

chip_type = '0007'

#
# Chip setup
#
# bit 0-4 always 0
# bit 5  USB remote wakeup
# bit 6  Self powered
# bit 7 always 1
#

chip_set='80'

#
# Max bus power
# max 500 ma
#

max_i = 500

# Chip setup 2
#           TYPE_AM      TYPE_BM             TYPE_2232C      TYPE_R          TYPE_2232H          TYPE_4232H
# bit 0         0      IsoIn              IsoIn part A       0               0                   0
# bit 1         0      IsoOut             IsoOut part A      0               0                   0
# bit 2         0      suspend_pull_down  suspend_pull_down              suspend_pull_down     suspend_pull_down
# bit 3         0      use_serial                                        use_serial            use_serial
# bit 4         0      change_usb_ver     change_usb_ver
# bit 5         0        0                IsoIn part B       0               0                   0
# bit 6         0        0                IsoOut part B      0               0                   0
# bit 7 always  0
#

chip_set2='08'

#
# TYPE_R Bitmask Invert, 0 else
#
# TYPE_4232H rs485enable
#  True/False
#

portA_485 = False
portB_485 = False
portC_485 = False
portD_485 = False

#
# Port settings
# 4ma  - 0
# 8ma  - 1
# 12ma - 2
# 16ma - 3
# SlowSlew - True/False
# SchmittInput - True/False
# 

portA_AL = 0
portA_AL_slow = False
portA_AL_schmitt = False

portB_AH = 0
portB_AH_slow = False
portB_AH_schmitt = False

portC_BL = 1
portC_BL_slow = False
portC_BL_schmitt = False

portD_BH = 1
portD_BH_slow = False
portD_BH_schmitt = False


#
#  Vendor  offset
#  Vendor  length (n  -  unicode characters)
#    length = (n+1)*2 bytes
#

vendor_off = 0x9a
vendor_len = (len(va)+1)*2


#
#  Product  offset
#  Product  length (n  -  unicode characters)
#    length = (n+1)*2 bytes
#

product_off = 0x9a + vendor_len
product_len = (len(pa)+1)*2


#
#  Serial  offset
#  Serial  length (n  -  unicode characters)
#    length = (n+1)*2 bytes
#

serial_off = 0x9a + vendor_len + product_len
serial_len = (len(sa)+1)*2

if vendor_len + product_len + serial_len > 96:
    print('Error: The size of the vendor+product+serial area is large.')
    exit()


#  Byte.BIT| TYPE_AM TYPE_BM   TYPE_2232C   TYPE_R       TYPE_2232H       TYPE_4232H
#  14.3:0  | UA      UA        CHIP         CBUS[0]      AL               A
#  14.7:0  | UA      UA        CHIP         CBUS[1]      AH               B

byte14 = '0'

#  15.3:0  | UA      UA        0            CBUS[2]      BL               C
#  15.7:0  | UA      UA        0            CBUS[3]      BH               D

byte15 = '0'

#  16.3:0  | UA      UA        UA           CBUS[4]      0                0
#  16.7:0  | UA      UA        UA           0            0                0

byte16 = '0'

#  17        UA      UA        UA           0            0                0

byte17 = '0'

#                                                        CHIP values:
#                                                        0x46: EEPROM is a 93xx46  128 bytes
#                                                        0x56: EEPROM is a 93xx56  256 bytes
#                                                        0x66: EEPROM is a 93xx66  512 bytes
#  18        UA      UA        UA           VENDOR       CHIP             CHIP

chip = '66'

#  19        UA      UA        UA           VENDOR       0                0

byte19 = '0'

#  1a        UA (all)

userarea = ua

vendorarea = bytes(va,'utf-16')

productarea = bytes(pa,'utf-16')

serialarea = bytes(sa,'utf-16')

#  Additional fields after the serial string:
#  0x00, 0x00 - reserved for "legacy port name prefix"
#  0x00, 0x00 - reserved for plug and play options
#  (Observed values with PnP == 0:
#  0x02 0x03 0x01 0x00)

legacy_port_name_prefix = '0000' # 0203
pnp_options = '0000' # 0100

#  Note: The additional fields after the serial number string
#  collide with the official FTDI formula from AN_121 regarding
#  the start of the user area:
#  "Start Address = the address following the last byte of SerialNumber string."

if chip == '66' :
    eeprom = [0] * 512
    eeprom[0x18] = int(chip,base=16)
elif chip == '56':
    eeprom = [0] * 256
    eeprom[0x18] = int(chip,base=16)
else:
    print('Not support  ',chip)
    exit()

eeprom[0] = ((ch_1 & 0xf)<<4 | (ch_0 & 0xf)) & 0xff
eeprom[1] = ((ch_3 & 0xf)<<4 | (ch_2 & 0xf)) & 0xff
eeprom[2] = int(idVendor[2:],base=16)
eeprom[3] = int(idVendor[0:2],base=16)
eeprom[4] = int(idProduct[2:],base=16)
eeprom[5] = int(idProduct[0:2],base=16)
eeprom[6] = int(chip_type[0:2],base=16)
eeprom[7] = int(chip_type[2:],base=16)
eeprom[8] = int(chip_set,base=16)
eeprom[9] = max_i // 2
eeprom[10] = int(chip_set2,base=16)
eeprom[11] = portA_485<<4 | portB_485<<5 | portC_485<<6 | portD_485<<7
eeprom[12] = (portA_AL & 3) | portA_AL_slow<<2 | portA_AL_schmitt<<3 | (portB_AH & 3)<<4 | portB_AH_slow<<6 | portB_AH_schmitt<<7
eeprom[13] = (portC_BL & 3) | portC_BL_slow<<2 | portC_BL_schmitt<<3 | (portD_BH & 3)<<4 | portD_BH_slow<<6 | portD_BH_schmitt<<7
eeprom[14] = vendor_off & 0xff
eeprom[15] = vendor_len & 0xff
eeprom[16] = product_off & 0xff
eeprom[17] = product_len & 0xff
eeprom[18] = serial_off & 0xff
eeprom[19] = serial_len & 0xff
eeprom[20] = int(byte14,base=16)
eeprom[21] = int(byte15,base=16)
eeprom[22] = int(byte16,base=16)
eeprom[23] = int(byte17,base=16)
eeprom[25] = int(byte19,base=16)

n=0x1a

for i in range(128):
    eeprom[n]=ua[i]
    n=n+1

if n != 0x9a:
    print('Error vendor area!')
    exit()

eeprom[n]=vendor_len & 0xff
n+=1
eeprom[n]=3
n+=1
for i in range(len(vendorarea)-2):
    eeprom[n]=vendorarea[i+2]
    n+=1

eeprom[n]=product_len & 0xff
n+=1
eeprom[n]=3
n+=1
for i in range(len(productarea)-2):
    eeprom[n]=productarea[i+2]
    n+=1

eeprom[n]=serial_len & 0xff
n+=1
eeprom[n]=3
n+=1
for i in range(len(serialarea)-2):
    eeprom[n]=serialarea[i+2]
    n+=1


eeprom[n] = int(legacy_port_name_prefix[0:2],base=16)
n+=1
eeprom[n] = int(legacy_port_name_prefix[2:],base=16)
n+=1
eeprom[n] = int(pnp_options[0:2],base=16)
n+=1
eeprom[n] = int(pnp_options[2:],base=16)
n+=1


checksum=0xaaaa
for i in range(0,len(eeprom)-2,2):
    v=eeprom[i+1]<<8 | eeprom[i]
    checksum=v^checksum
    checksum=((checksum << 1)|(checksum >> 15)) & 0xffff
eeprom[254] = checksum & 0xff
eeprom[255] = (checksum >> 8) & 0xff

with open(eeprom_name,mode='wb') as f:
    f.write(bytes(eeprom))

print("OK! Write ",eeprom_name)

# for i in range(len(eeprom)):
#     if i%16 == 0:
#         print('')
#     print('{0:0>2x} '.format(eeprom[i]),end='')

# print('')

