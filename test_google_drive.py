"""
Test Google Drive API - Sprawdzanie dostępu do folderu
"""
import os
import sys

# Fix dla Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("[TEST] GOOGLE DRIVE API")
print("=" * 60)

# Krok 1: Sprawdź czy jest plik credentials
print("\n📁 Krok 1: Sprawdzanie pliku credentials...")

# Zmień ścieżkę do twojego pliku JSON
CREDENTIALS_PATH = r"C:\Users\rymko\Desktop\CLAUDE\oferta kompletna\AOP+++\sixth-arbor-471809-m2-209ff1b2b2d1.json"

if not os.path.exists(CREDENTIALS_PATH):
    print(f"❌ BŁĄD: Nie znaleziono pliku: {CREDENTIALS_PATH}")
    print("\n💡 Co zrobić:")
    print("1. Pobierz JSON key z Google Cloud Console")
    print("2. Zapisz na Pulpicie jako 'service-account.json'")
    print("3. Uruchom ponownie ten skrypt")
    sys.exit(1)

print(f"✅ Plik znaleziony: {CREDENTIALS_PATH}")

# Krok 2: Zainstaluj bibliotekę (jeśli trzeba)
print("\n📦 Krok 2: Sprawdzanie biblioteki google-api-python-client...")

try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    print("✅ Biblioteka zainstalowana")
except ImportError:
    print("❌ Brak biblioteki google-api-python-client")
    print("\n💡 Instaluję teraz...")
    os.system("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    print("\n🔄 Uruchom skrypt ponownie po instalacji")
    sys.exit(0)

# Krok 3: Połączenie z Google Drive
print("\n🔗 Krok 3: Łączenie z Google Drive API...")

try:
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    print("✅ Połączono z Google Drive API")
except Exception as e:
    print(f"❌ Błąd połączenia: {e}")
    sys.exit(1)

# Krok 4: Test odczytu folderu
print("\n📂 Krok 4: Sprawdzanie dostępu do folderu...")

FOLDER_ID = "1v28sAIP0x85qze38BynAHweDpPKhinB6"

try:
    # Pobierz informacje o folderze
    folder = service.files().get(fileId=FOLDER_ID, fields='id, name, mimeType').execute()
    print(f"✅ Dostęp do folderu: {folder['name']}")
    print(f"   ID: {folder['id']}")

    # Lista plików w folderze
    print("\n📄 Lista plików w folderze:")
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents",
        pageSize=10,
        fields="files(id, name, mimeType)"
    ).execute()

    items = results.get('files', [])

    if not items:
        print("   ⚠️ Folder jest pusty")
    else:
        for item in items:
            icon = "📁" if item['mimeType'] == 'application/vnd.google-apps.folder' else "📄"
            print(f"   {icon} {item['name']}")

    print("\n" + "=" * 60)
    print("🎉 SUKCES! Google Drive API działa!")
    print("=" * 60)
    print("\n✅ Service Account ma dostęp do folderu")
    print("✅ Możesz użyć tych credentials w Streamlit Cloud")

except Exception as e:
    print(f"❌ Błąd dostępu do folderu: {e}")
    print("\n💡 Co może być nie tak:")
    print("1. Folder nie został udostępniony dla service account")
    print("2. Email service account: streamlit-drive-reader@sixth-arbor-471809-m2.iam.gserviceaccount.com")
    print("3. Sprawdź czy email jest dokładnie taki sam")
    print("4. Uprawnienia: 'Viewer' (Przeglądający)")
    sys.exit(1)
