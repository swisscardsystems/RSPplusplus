import getpass
import pkcs11
from pkcs11 import Attribute, ObjectClass, KeyType, Mechanism, KDF

lib = pkcs11.lib("/opt/safenet/protecttoolkit7/ptk/lib/libcryptoki.so")

with open("server_pub.bin", "rb") as file:
    server_pub_bytes = file.read()

# Strip the ASN.1 OCTET STRING header (0x04 0x41) if present
if len(server_pub_bytes) == 67 and server_pub_bytes.startswith(b'\x04\x41'):
    server_pub_bytes = server_pub_bytes[2:]

token = lib.get_token(token_label='OPERATOR')
user_pin = getpass.getpass(prompt="Enter PIN: ")

with token.open(user_pin=user_pin, rw=True) as session:
    operator_priv_key = session.get_key(label='DH_KEY_OPERATOR', object_class=ObjectClass.PRIVATE_KEY)

    # THE FIX: Define the Thales PROPRIETARY NIST KDF Constant
    CKD_SHA256_NIST_KDF_THALES = 0x80000014

    print("Deriving KEK using ECDH...")
    operator_kek = operator_priv_key.derive_key(
        KeyType.AES, 256,
        mechanism=Mechanism.ECDH1_DERIVE,
        mechanism_param=(CKD_SHA256_NIST_KDF_THALES, None, server_pub_bytes),
        template={
            Attribute.LABEL: "ECDH_KEK_OPERATOR",
            Attribute.SENSITIVE: True,
            Attribute.EXTRACTABLE: False,
            Attribute.TOKEN: False,
            Attribute.WRAP: True
        }
    )

    print("Load transport key...")
    transport_key = session.get_key(label='TRANSPORT_KEY', object_class=ObjectClass.SECRET_KEY)
    # print("Generate transport key...")
    # transport_key = session.generate_key(
    #     KeyType.AES, 256,
    #     template={
    #         Attribute.LABEL: "TRANSPORT_KEY",
    #         Attribute.SENSITIVE: True,
    #         Attribute.EXTRACTABLE: True,
    #         Attribute.ENCRYPT: True,
    #         Attribute.DECRYPT: True,
    #         Attribute.TOKEN: True
    #     }
    # )

    # Mechanism.AES_KEY_WRAP implements RFC 3394, which is the FIPS standard for key wrapping
    print("Wrapping transport key...")
    encrypted_key_blob = operator_kek.wrap_key(
        transport_key,
        mechanism=Mechanism.AES_KEY_WRAP
    )

    with open("operator_encrypted_key.bin", "wb") as file:
        file.write(encrypted_key_blob)

    print("Success! Encrypted key blob: {encrypted_key_blob.hex()}")
