import json
from google.cloud import  storage
from google.cloud import translate_v3 as translate
import requests

project_id="fluid-unfolding-412101"
location = "us-central1"


def delete_glossary(
    timeout: int = 180,
) -> translate.Glossary:
    """Delete a specific glossary based on the glossary ID.

    Args:
        project_id: The ID of the GCP project that owns the glossary.
        glossary_id: The ID of the glossary to delete.
        timeout: The timeout for this request.

    Returns:
        The glossary that was deleted.
    """
    client = translate.TranslationServiceClient()

    name = client.glossary_path(project_id, location, glossary_id)

    operation = client.delete_glossary(name=name)
    result = operation.result(timeout)
    print(f"Deleted: {result.name}")

    return result

def upload_glossary_to_bucket(bucket_name: str, glossary_file_path: str, destination_blob_name: str):
    """Uploads a glossary file to the specified Google Cloud Storage bucket."""
    storage_client = storage.Client(project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(glossary_file_path)
    print(f"File {glossary_file_path} uploaded to {destination_blob_name}.")

def upload_glossary(uri,target_language):

    url = f'https://translation.googleapis.com/v3/projects/{project_id}/locations/{location}/glossaries'
    # print(os.environ["ACCESS_TOKEN"])
    headers = {
        "Authorization": f"Bearer ya29.a0AfB_byDY3Var3uN_hMS8PNRteTArEYQja-ar7mvy_u0tXUshqFbguSlG19hj9pw8OSg7yUKKtUQAr0wfMED5X9oT5C4oyYeUZN0C5yI8B6OLzuKTQR6epHxvQWz0-xVxm3Qpk7XkVxQbOpBGMKoJ4HVa6iBkUKLNESEX6vHj2ngaCgYKAUASARISFQHGX2MiqenbVnQQ1_Xie1Hw3vHycQ0178",
        "Content-Type": "application/json; charset=utf-8",
        "x-goog-user-project": "fluid-unfolding-412101"
    }

    data = {
        "name": f"projects/{project_id}/locations/{location}/glossaries/{glossary_id}",
        "languagePair": {
            "sourceLanguageCode": "en",
            "targetLanguageCode": target_language
        },
        "inputConfig": {
            "gcsSource": {
                "inputUri": uri
            }
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        print("Status code:", response.status_code)
        print("Response:", response.text)
        print("Glossary uploaded successfully.")
    elif response.status_code == 409:
        delete_glossary()
        upload_glossary(uri, target_language)

    return response



def main(glossary_id: str,bucket_name, target_language):
    glossary_file_name = f"{glossary_id}.csv"
    glossary_file_path = f"./glossaries/{glossary_file_name}"
    destination_blob_name = f"glossaries/{glossary_file_name}"
    upload_glossary_to_bucket(bucket_name, glossary_file_path, destination_blob_name)

    glossary_uri = f"gs://{bucket_name}/{destination_blob_name}"
    upload_glossary(glossary_uri, target_language)


if __name__=="__main__":
    bucket_name = "translation-glossaries-updraft"
    glossary_id ="en_it_glossary"
    target_language="it"
    main(glossary_id,bucket_name, target_language)
# Example usage



