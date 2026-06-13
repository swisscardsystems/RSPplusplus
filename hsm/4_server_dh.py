import getpass, pkcs11
from pkcs11 import Attribute, ObjectClass, KeyType, Mechanism, KDF

lib = pkcs11.lib("/opt/safenet/protecttoolkit7/ptk/lib/libcryptoki.so")

with open("operator_pub.bin", "rb") as file:
    op_pub_bytes = file.read()

# The blob received from the Operator over the network
# encrypted_key_blob = bytes.fromhex("ENCRYPTED_KEY_BLOB")

with open("operator_encrypted_key.bin", "rb") as file:
    encrypted_key_blob = file.read()

token = lib.get_token(token_label='SERVER')
user_pin = getpass.getpass(prompt="Enter PIN: ")

with token.open(user_pin=user_pin, rw=True) as session:
    server_priv_key = session.get_key(label='DH_KEY_SERVER', object_class=ObjectClass.PRIVATE_KEY)

    CKD_SHA256_NIST_KDF_THALES = 0x80000014

    print("Deriving KEK using ECDH...")
    server_kek = server_priv_key.derive_key(
        KeyType.AES, 256,
        mechanism=Mechanism.ECDH1_DERIVE,
        mechanism_param=(CKD_SHA256_NIST_KDF_THALES, None, op_pub_bytes),
        template={
            Attribute.LABEL: "ECDH_KEK_SERVER",
            Attribute.SENSITIVE: True,
            Attribute.EXTRACTABLE: False,
            Attribute.TOKEN: False,
            Attribute.UNWRAP: True
        }
    )

    print("Unwrapping transport key...")
    transport_key = server_kek.unwrap_key(
        object_class=ObjectClass.SECRET_KEY,
        key_type=KeyType.AES,
        key_data=encrypted_key_blob,
        mechanism=Mechanism.AES_KEY_WRAP,
        template={
            Attribute.LABEL: "VENDOR_18_AES256",
            Attribute.SENSITIVE: True,
            Attribute.EXTRACTABLE: False,
            Attribute.TOKEN: True,
            Attribute.ENCRYPT: True,
            Attribute.DECRYPT: True
        }
    )

    print("Success! Transport key securely established.")
