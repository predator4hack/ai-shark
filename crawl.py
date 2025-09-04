import requests
from bs4 import BeautifulSoup

# === CONFIGURATION ===
# The readonly link you have
VIEW_LINK = "https://drive.google.com/file/d/16p8InLz7fl4OV2LXHKbLSGlVP7X34uUm/view"

# The cookie you copied from your browser's developer tools.
# This is crucial for authentication. Format: 'S=your_cookie_value; NID=another_value'
YOUR_COOKIE = 'HSID=AcTs0_osnQF4sMGhr;SSID=AIP9y874VHLQkIAWG;APISID=OyGoNtsoFOg_lNUH/AOb_TieXvgXmr3Vf9;SAPISID=O6VQESFL58d_eA3m/AS4nDKQrRF1Fg6p0l;__Secure-1PAPISID=O6VQESFL58d_eA3m/AS4nDKQrRF1Fg6p0l;__Secure-3PAPISID=O6VQESFL58d_eA3m/AS4nDKQrRF1Fg6p0l;SEARCH_SAMESITE=CgQIn54B;SID=g.a0000QhUZual_UIaEvLqiOVIbDKTgst_1x4QyY5JNxDfO35Tz7PXPlS8xXRNVAsQwQ9pTL6bVQACgYKAboSARYSFQHGX2MiH6TJdAg5QM0zMd2l8ETODxoVAUF8yKo3CnNrlmnHQn-sUPqg_Gma0076;__Secure-1PSID=g.a0000QhUZual_UIaEvLqiOVIbDKTgst_1x4QyY5JNxDfO35Tz7PXFCm8g3W4UH40hdBYbtDneQACgYKAX4SARYSFQHGX2MidsiMeq6ecSp56x0weMuAtBoVAUF8yKrIuAFiJ9v6tHqhBYrN6xxx0076;__Secure-3PSID=g.a0000QhUZual_UIaEvLqiOVIbDKTgst_1x4QyY5JNxDfO35Tz7PXfXvmaY5gOj4qvZ67YPHulwACgYKAcASARYSFQHGX2Mi7vlq3ZWucZkB9s6iu95pgRoVAUF8yKpoGFiE0DARxFz_jsz3-A2r0076;OSID=g.a0001AhUZpESU8D45ovZ7OSEvwnhNsZno7p25N5E0T_Hl3Suw9HX2nKQwkIdC8hkjFDo3YaujAACgYKAXMSARYSFQHGX2MihmDqrm8J7ZPd21iN_9xqlxoVAUF8yKrgA5FuRY3n8J4bIjBwPsM50076;__Secure-OSID=g.a0001AhUZpESU8D45ovZ7OSEvwnhNsZno7p25N5E0T_Hl3Suw9HXMPlnqB4lNO7CU_S_NxaZuAACgYKAbISARYSFQHGX2MiCKKwE7oRPOf7LfgNQgsyzRoVAUF8yKrBruLXj1VKoqXe1QRKpTTv0076;COMPASS=photos-fife=CgAQ273nxQYaWAAJa4lXKMVTLcj_DQAhv27kpp5hcMbduDowJwhQ2IzBbLbE4glZmYppw2RlE4TDPsG2f1VLhJTxHQxehOPq1A3mJzhOz3rWWKpV6qC3_GoJirYnYf7kWbEwAQ;__Secure-1PSIDTS=sidts-CjIB5H03P_rjr5M-OPqZ7Xfx3VtBd3eoYOENCVdHPj2-LfMgTQNDhzVTJG47NlkR1llELRAA;__Secure-3PSIDTS=sidts-CjIB5H03P_rjr5M-OPqZ7Xfx3VtBd3eoYOENCVdHPj2-LfMgTQNDhzVTJG47NlkR1llELRAA;AEC=AVh_V2g49d0KCJiPhajC9zphD6SL_8oopOA7vMzVowGYm9LwFfDcKPoGBBQ;NID=525=nWDU4fHbuc5nSxUA_HVJdZNhjbwX2Vv1ccMaIXr-NvBA3LC9iIi8EL_qJsJELVguhaqRo0joWeonmW6kYyzvlzoS5--72W5wa381jQzHJ5YXbAmTf_uZ3W0Xq8Nd_nbf5PWt2Xwsh8C11qiFjOxEEtPs_OOVH_fIMbJywZm7GlpsqAs0xRenG193f5ohtlK08vDqI22v-JLLZMrCT2Qicz1MQ_RxZgYnn1siQo02xSkSGJE_lBmEWLRsr-yU9bYyBtbCd123vRnkPL8ajzWcI5BuhtAG_V2_8r50OYi0cnkZ7Dc2nEYpc79mG-0SDS-dlbqMTGGApJXTYd3VCMmuciAUfsExV6bcl-QNQ-ThsvMudLd50pWuHnJNY0g2atDHVsq1Y8S3dfxktVM_7TtDa8rIVVRNLXeJMO3DoIbMZMV_w84C083OHVf0U9lSLzKjtjk-P5-pLQ9ZL2ed7BLgO4il8LQszP2AQFkfmOo5nB7Kj1Xib2rxnzw2R-0LY68MGCNpN0yRCrGgAKzWZVY_dbMGn_3tKKtZRZmJEm4FUgQ9JqBLl9Gl8n7wQxWp5atxy9BnvalOivOLEKtPE4crcv55fQEbeJ_-uitA2eamf3d9I_-rxk3IpLau21HfMI4tBanrSEdaYTCL6_WCYOV16J_Ga5b9fop0fBquTyeYDK6H2Na6CBsob3DI_WTc90lDUsdNv9oM0DfRuAi0mBKcXtRdTAtqJs46ZJ2V2KL7r9tzr8nQ-jWVBQMRfD_I0LP30ePYV6z9PXYvFMLQqNssbQ-daBO7c21_Qnq0OS2itBWV;SIDCC=AKEyXzVxw5USsunoLrKAME1fgVvlZXqfnEfbUcAjhTZ6GKMqLMkQSDlTq1-rdLM-iySg6qQglUM;__Secure-1PSIDCC=AKEyXzWlVDcKxLjLIgIIFZ-EPFHfTwAFOm2RL7wK4WxOY3izoVRwbe6xDOu54DKRxUMH8RGVM4Q;__Secure-3PSIDCC=AKEyXzXV95sPfixKJ0tUkqps4bzcr306qTi9-AbrhBhApfQNQ7Mmg1m9puDwAy1mrwyj7VLOZ6o'

# The desired output filename
OUTPUT_FILENAME = "my_recovered_document.pdf"
# === END CONFIGURATION ===

headers = {
    'authority': 'drive.google.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': YOUR_COOKIE,  # The script uses your authenticated session
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-arch': '"x86"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

# 1. First, make a request to the view link to get the HTML page.
session = requests.Session()
response = session.get(VIEW_LINK, headers=headers)
response.raise_for_status()  # Crash if the request failed

# 2. Parse the HTML to find the download form and extract the confirmation token.
soup = BeautifulSoup(response.text, 'html.parser')
form = soup.find('form', id='download-form')
if not form:
    print("Could not find the download form on the page. The structure might have changed.")
    exit(1)

# The action URL is often a generic /uc?export=download endpoint
action_url = form.get('action')
# Find the hidden input with the name 'confirm'
confirm_input = form.find('input', {'name': 'confirm'})
if not confirm_input:
    print("Could not find the confirmation token. The page might be asking for a CAPTCHA or the cookie is invalid.")
    exit(1)

confirm_value = confirm_input.get('value')
# Prepare the data to be posted
data = {
    'confirm': confirm_value,
    'id': form.find('input', {'name': 'id'}).get('value'),
    'uuid': form.find('input', {'name': 'uuid'}).get('value'),
}

# 3. Make a POST request to the download URL with the confirmation token.
# We stream the response so we can handle large files.
download_url = 'https://drive.google.com' + action_url
print(f"Requesting PDF from: {download_url}")
download_response = session.post(download_url, headers=headers, data=data, stream=True)
download_response.raise_for_status()

# 4. Check if the response is actually a PDF.
content_type = download_response.headers.get('content-type')
if 'application/pdf' not in content_type:
    print(f"Unexpected response: {content_type}. The download may have failed or been redirected to a consent page.")
    # It's often helpful to see the first 500 characters of the response for debugging.
    print(download_response.text[:500])
    exit(1)

# 5. Save the PDF stream to a file.
print(f"Saving PDF to {OUTPUT_FILENAME}...")
with open(OUTPUT_FILENAME, 'wb') as f:
    for chunk in download_response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)

print("Download complete!")