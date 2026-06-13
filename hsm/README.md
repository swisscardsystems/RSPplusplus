# Diffie-Hellman Key Exchange

## --- Step 0 (Restricted) ---
## Build And Run Container

```bash
docker compose build
docker compose up -d
docker exec -it dh-hsm-server bash
docker exec -it dh-hsm-operator bash
```

## Initialization

## --- Step 1.A ---
### Server: config HSM config

```bash
ctconf
# Admin SO pin: 11111111
# Administrator's pin: 22222222

ctident gen-selfsigned all
ctconf -fF

ctconf -n0
# label: SERVER
# Security Officer's pin: 33333333

ctkmu p -s0
# new user PIN for token in Slot 0: 44444444
```

## --- Step 1.B ---
### Server: generate ECDH keypair, export PUBLIC

```bash
ctkmu c -tec -C secp256r1 -n DH_KEY_SERVER -aTMR -s0
# CKA_SENSITIVE
# CKA_MODIFIABLE
# CKA_DERIVE

cd /app
python3 server_public_key.py
```

## --- Step 2.A ---
### Operator: perform HSM config

```bash
ctconf
# Admin SO pin: 11111111
# Administrator's pin: 22222222

ctident gen-selfsigned all
ctconf -fF

ctconf -n0
# label: OPERATOR
# Security Officer's pin: 33333333

ctkmu p -s0
# new user PIN for token in Slot 0: 44444444
```

## --- Step 2.B ---
### Operator: generate ECDH keypair, export PUBLIC

```bash
ctkmu c -tec -C secp256r1 -n DH_KEY_OPERATOR -aTMR -s0
# CKA_SENSITIVE
# CKA_MODIFIABLE
# CKA_DERIVE

cd /app
python3 operator_public_key.py
```
## --- Step 2.C ---
### Operator: generate TANSPORT key

```bash
ctkmu c -taes -z256 -n TRANSPORT_KEY -aTEDX -s0
# CKA_SENSITIVE
# CKA_ENCRYPT
# CKA_DECRYPT
# CKA_EXTRACTABLE
```


## --- Step 3.A ---
### Operator: Export wrapped TK

```bash
# Operator
cd /app
python3 operator_dh.py
```

## --- Step 3.B ---
### Server: Import wrapped TK

```bash
cd /app
python3 server_dh.py
```

## --- Step 4 ---
### Server: Calculate KCV

```bash
cd /app
python3 5_server_kcv.py
```

## --- Links ---
* [ProtectToolkit-C mechanisms](https://thalesdocs.com/gphsm/ptk/protectserver3/docs/ps_ptk_docs/ptkc_programming/ptkc_mechs/index.html)
* [CKM_ECDH1_DERIVE](https://thalesdocs.com/gphsm/ptk/protectserver3/docs/ps_ptk_docs/ptkc_programming/ptkc_mechs/ckm_ecdh1_derive/index.html)
