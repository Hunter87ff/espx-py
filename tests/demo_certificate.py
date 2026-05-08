import os
import sys

# Ensure the local espx source is in the path
sys.path.insert(0, os.path.join(os.getcwd(), "python"))

from espx.client import ESPXClient
from espx.models import CertificateData, CertificateSocial

def main():
    # The server is running on localhost:8001
    # Note: Adding a dummy access_token since generate_url requires authentication
    client = ESPXClient(base_url="http://localhost:8001", access_token="sprucepointtable87")

    # Demo certificate data
    data = CertificateData(
        organizer="ESports X",
        eventname="Demo Championship 2026",
        date="2026-05-08",
        certificateno="DEMO-001",
        name="John Doe",
        rank=1,
        social=CertificateSocial(twitter="@espx_demo")
    )

    print("Generating demo certificate URL...")
    try:
        # Using generate_url which returns the CDN URL
        url = client.certificates.generate_url(data)
        print(f"Generated Certificate URL: {url}")
        
    except Exception as e:
        print(f"Error generating certificate: {e}")

if __name__ == "__main__":
    main()
