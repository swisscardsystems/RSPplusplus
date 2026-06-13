import getpass
import pkcs11
from pkcs11.constants import Attribute, ObjectClass

lib = pkcs11.lib("/opt/safenet/protecttoolkit7/ptk/lib/libcryptoki.so")

token = lib.get_token(token_label='OPERATOR')

user_pin = getpass.getpass(prompt="Enter User's PIN: ")

with token.open(user_pin=user_pin) as session:
    operator_pub_key = session.get_key(label='DH_KEY_OPERATOR', object_class=ObjectClass.PUBLIC_KEY)
    raw_pub_bytes = operator_pub_key[Attribute.EC_POINT]

    with open("operator_pub.bin", "wb") as file:
        file.write(raw_pub_bytes)

    print(f"Success! Extracted {len(raw_pub_bytes)} bytes.")
    print(f"Hex: {raw_pub_bytes.hex()}...")
