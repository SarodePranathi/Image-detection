import cv2
import requests
from requests.auth import HTTPBasicAuth
import os

API_KEY = 'enter your API key'
API_SECRET = 'enter your API secret'

def download_image(url, filename='downloaded.jpg'):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ Image downloaded as {filename}")
        return filename
    except Exception as e:
        print(f"❌ Failed to download image: {e}")
        return None

def capture_image(filename='captured.jpg'):
    print("📷 Opening webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Cannot access camera.")
        return None

    print("✅ Press SPACE to capture image or ESC to exit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame.")
            break
        cv2.imshow("Webcam - Press SPACE to Capture", frame)

        key = cv2.waitKey(10)
        if key == 27:
            print("⏹️ Escape pressed. Exiting without capture.")
            cap.release()
            cv2.destroyAllWindows()
            return None
        elif key % 256 == 32:
            cv2.imwrite(filename, frame)
            print(f"✅ Image saved as {filename}")
            break

    cap.release()
    cv2.destroyAllWindows()
    return filename

def recognize_image(image_path):
    print("📤 Uploading image to Imagga...")
    with open(image_path, 'rb') as image_file:
        upload_response = requests.post(
            'https://api.imagga.com/v2/uploads',
            auth=HTTPBasicAuth(API_KEY, API_SECRET),
            files={'image': image_file}
        )
    upload_data = upload_response.json()
    print("Upload Response:", upload_data)

    if 'result' not in upload_data:
        print("❌ Upload failed.")
        return

    upload_id = upload_data['result']['upload_id']

    print("🔍 Requesting tags from Imagga...")
    tag_response = requests.get(
        f'https://api.imagga.com/v2/tags?image_upload_id={upload_id}',
        auth=HTTPBasicAuth(API_KEY, API_SECRET)
    )

    if tag_response.status_code != 200:
        print("❌ Tag API failed. Response:", tag_response.text)
        return

    tag_data = tag_response.json()
    if 'result' not in tag_data:
        print("❌ No result in tag response.")
        return

    tags = tag_data['result']['tags']
    print("\n🏷️ Top 2 Tags:")
    for tag in tags[:2]:
        print(f"→ {tag['tag']['en']} (Confidence: {tag['confidence']:.2f})")

def main():
    choice = input("Type 'capture' to use webcam or 'upload' to select an image file or URL: ").strip().lower()
    
    if choice == 'capture':
        image_path = capture_image()
        if image_path:
            recognize_image(image_path)
            print("\n✅ Done!")
        else:
            print("No image captured. Exiting.")
    elif choice == 'upload':
        image_path = input("Enter full path of the image file or image URL: ").strip()
        if image_path.startswith('http://') or image_path.startswith('https://'):
            image_path = download_image(image_path)
            if not image_path:
                print("Download failed. Exiting.")
                return
        elif not os.path.isfile(image_path):
            print("❌ File does not exist. Exiting.")
            return
        
        recognize_image(image_path)
        print("\n✅ Done!")
    else:
        print("Invalid choice. Please run again and type 'capture' or 'upload'.")

if __name__ == "__main__":
    main()
