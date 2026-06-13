import getpass, pkcs11
from pkcs11 import ObjectClass, Mechanism

# 1. Initialize the PKCS#11 driver/module
# Replace with the path to your vendor's shared library (.so, .dll, or .dylib)
lib = pkcs11.lib("/opt/safenet/protecttoolkit7/ptk/lib/libcryptoki.so")

# 2. Get the specific cryptographic token
token = lib.get_token(token_label="SERVER")
user_pin = getpass.getpass(prompt="Enter PIN: ")

# 3. Open a session and log in using your User PIN
with token.open(user_pin=user_pin, rw=True) as session:
    
    # 4. Find your existing encryption key on the token
    # (Alternatively, you can generate one using session.generate_key)
    key = session.get_key(
        object_class=ObjectClass.SECRET_KEY, 
        label="TRANSPORT_KEY"
    )
    
    # 5. Define your array / data structure
    data_array = [0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0]
    # data_array = [1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1]

    # 6. Convert array to bytes (Symmetric encryption requires a byte string)
    data_bytes = bytes(data_array)

    # 7. Perform the encryption
    ciphertext = key.encrypt(
        data_bytes,
        mechanism=Mechanism.AES_ECB,
    )
    
    print(f"KCV (Hex): {ciphertext[:3].hex()}")
    