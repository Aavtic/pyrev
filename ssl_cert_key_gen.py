from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime

# Generate a private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Generate a self-signed certificate
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, input("Enter Country Name: ")),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME,
                       input("Enter State or Privince Name: ")),
    x509.NameAttribute(NameOID.LOCALITY_NAME,
                       input("Enter Locality Name: ")),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME,
                       input("Enter Organization Name: ")),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])

certificate = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName("localhost")]),
    critical=False,
).sign(private_key, hashes.SHA256())

# Save the private key to a file
with open("private.key", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))

# Save the certificate to a file
with open("cert.pem", "wb") as f:
    f.write(certificate.public_bytes(serialization.Encoding.PEM))

print("Self-signed certificate and private key generated.")
