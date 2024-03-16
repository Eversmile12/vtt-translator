import os
import re
import time
from multiprocessing import Pool
from google.cloud import translate
import google.api_core.exceptions
# from google.cloud import translate_v2 as translate

# @dev: This function scans a given directory for files and determines which of the expected languages are missing translations.
# @params: 
#     folder_path: str - The path to the directory containing translation files.
#     existing_languages: list - A list of language codes representing the expected set of translations.

def get_missing_languages(folder_path, existing_languages):
    """Returns a list of languages that don't have a translation in the folder."""
    # Get all files in the directory
    files = os.listdir(folder_path)
    missing_languages = existing_languages.copy()
    for file in files:
        for lang in existing_languages:
            if f"-{lang.upper()}" in file:
                missing_languages.remove(lang)
                break
    return missing_languages

# @dev Translates a list of text segments to a specified target language using Google Cloud Translate API v2.
# @params
#     target_language: str - The ISO 639-1 code of the target language.
#     segments: list - A list of strings to be translated.

def translate_text_v2(target_language,segments: []) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate.Client()
    translated_segments = []
    # glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)
    retry_delay = 1  # Initial delay in seconds
    max_retries = 10  # Maximum number of retries
    for segment in segments:
        if isinstance(segment, bytes):
            segment = segment.decode("utf-8")
        for attempt in range(max_retries):

            try:
                    result = translate_client.translate(segment, target_language=target_language)
                    translated_text = result["translatedText"]
                    break  # Break the loop if successful
            except google.api_core.exceptions.ResourceExhausted:
                    if attempt < max_retries - 2:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    elif attempt < max_retries - 1:
                        time.sleep(120)
                    else:
                        raise  # Re-raise the exception if max retries reached
            except:
                translated_text = "[BLANK_AUDIO]"
                break
        if translated_text:
            translated_segments.append(translated_text)
        else: 
            translated_segments.append("[BLANK_AUDIO]")

    return translated_segments

# @dev Translates a list of text segments to a specified target language, using advanced features like glossaries if applicable, via Google Cloud's Translation API v3.
# @params
#     target_language: str - The ISO 639-1 code of the target language.
#     segments: list - A list of strings to be translated.

def translate_text_v3(target_language: str, segments: list) -> list:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate.TranslationServiceClient()

    location = "us-central1"
    project_id = "fluid-unfolding-412101"
    parent = f"projects/{project_id}/locations/{location}"
    glossary_name = f"en_{target_language.lower()}_glossary"
    translated_segments = []
    if target_language == "es" or target_language == "it":
        glossary = translate_client.glossary_path(
            project_id, "us-central1", glossary_name  # The location of the glossary
        )

        glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)

    retry_delay = 1  # Initial delay in seconds
    max_retries = 10  # Maximum number of retries

    for segment in segments:
        if isinstance(segment, bytes):
            segment = segment.decode("utf-8")
        result = None  # Initialize result
        for attempt in range(max_retries):
            try:
                
                if target_language == "es" or target_language == "it":
                    result = translate_client.translate_text(
                        request={
                            "parent": parent,
                            "contents": [segment],
                            "mime_type": "text/plain",
                            "source_language_code": "en",
                            "target_language_code": target_language,
                            "glossary_config": glossary_config
                        }
                    )
                else:
                    result = translate_client.translate_text(
                    request={
                        "parent": parent,
                        "contents": [segment],
                        "mime_type": "text/plain",
                        "source_language_code": "en-US",
                        "target_language_code": target_language,
                    }
                )
                break  # Break the loop if successful
            except google.api_core.exceptions.ResourceExhausted:
                if attempt < max_retries - 2:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                elif attempt < max_retries - 1:
                    time.sleep(120)
                else:
                    raise  # Re-raise the exception if max retries reached
            except Exception as e:  # Catch other exceptions
                print(f"Glossary error: {e}, {target_language}, \n {glossary_config}")
                translated_segments.append("[ERROR]")  # Handle the error case
                break  # Exit the loop on error
        if result:  # Check if result was successfully assigned
            for translation in result.translations:
                translated_text = translation.translated_text if translation.translated_text else "[BLANK_AUDIO]"
                translated_segments.append(translated_text)
        else:
            translated_segments.append("[BLANK_AUDIO]")  # Handle cases where translation was not successful

    return translated_segments

# @dev Processes a single .vtt (Video Text Tracks) file, extracting text segments for translation and then saving the translated text back into a new .vtt file.
# @params
#     args: tuple - A tuple containing the path to the .vtt file and the target language code.
#     error_list: list - A reference to a list where error messages can be appended.
def process_vtt(args,error_list):
    file_path, target_language = args
    print(f"Translating '{file_path}' into: {target_language}")

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    timestamps = []
    text_segments = []
    text_buffer = []
    skip_header = True

    for line in lines:
        if skip_header and line.strip() == "WEBVTT":
            skip_header = False
            continue
        # Skip index lines
        if line.strip().isdigit():
            continue

        # Process timestamp and text lines
        if re.match(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line):
            if text_buffer:
                text_segments.append(' '.join(text_buffer))
                text_buffer = []
            timestamps.append(line.strip())
        elif line.strip():
            text_buffer.append(line.strip())

    if text_buffer:
        text_segments.append(' '.join(text_buffer))

    # Join, translate, and split back as before
        

    translated_segments = translate_text_v3(target_language,text_segments)

    try:
        if len(translated_segments) != len(timestamps):
            error_message = f"File: {file_path}, Lang: {target_language} - Segment count mismatch f{len(translated_segments)} f{len(timestamps)}"
            error_list.append(error_message)
            print(error_message)
            return  # Skip the translation for this file
        # Rest of the existing process_vtt function code for writing the translated file
    except Exception as e:
        error_list.append(f"File: {file_path}, Lang: {target_language} - Error: {str(e)}")
        print(f"Error processing file: {file_path}, Lang: {target_language}")

    # Write to new file in translated folder
    base_name = os.path.basename(file_path)
    name_without_extension = os.path.splitext(base_name)[0]
    name_without_language = re.sub(r'-[A-Z]{2}$', '', name_without_extension)
    translated_file_name = f"{name_without_language}-{target_language.upper()}.vtt"

    # Save the translated file in the same directory as the original file
    translated_file_path = os.path.join(os.path.dirname(file_path), translated_file_name)
    with open(translated_file_path, 'w', encoding='utf-8') as file:
        index = 1  # Start index counter
        file.write("WEBVTT\n\n")
        for timestamp, text in zip(timestamps, translated_segments):
            file.write(str(index) + '\n')
            file.write(timestamp + '\n')
            file.write(text + '\n\n')
            index += 1


# @dev Sequentially processes all .vtt files within a specified folder that require translation, for a set of given languages.
# @params
#     folder_path: str - The root directory to search for .vtt files.
#     existing_languages: list - A list of language codes representing the expected set of translations.
def batch_translate_vtt_folder(folder_path, existing_languages):
    for root, dirs, files in os.walk(folder_path):
        english_vtt = None
        for file in files:
            if file.endswith('-EN.vtt'):
                english_vtt = os.path.join(root, file)
                break

        if english_vtt:
            missing_languages = get_missing_languages(root, existing_languages)
            if missing_languages:
                print(f"Translating '{english_vtt}' into: {missing_languages}")
                process_vtt(english_vtt, missing_languages)

# @dev Uses multiprocessing to process all .vtt files within a specified folder that require translation, for a set of given languages.
# @params
#     folder_path: str - The root directory to search for .vtt files.
#     existing_languages: list - A list of language codes representing the expected set of translations.
def multi_process_batch_translate_vtt_folder(folder_path, existing_languages):
    pool = Pool()  # Create a pool of worker processes
    tasks = []
    error_list = []

    for root, dirs, files in os.walk(folder_path):
        # Check for the presence of the English VTT file
        english_vtt = None
        for file in files:
            if file.endswith('-EN.vtt'):
                english_vtt = os.path.join(root, file)
                break

        # Proceed only if the English VTT file is found
        if english_vtt:
            missing_languages = get_missing_languages(root, existing_languages)
            if missing_languages:
                for lang in missing_languages:
                    tasks.append((english_vtt, lang))
       
    total_docs = len(tasks)
    pool.starmap(process_vtt, [(task, error_list) for task in tasks])
    pool.close()
    pool.join()

    translated_docs = total_docs - len(error_list)

    for error in error_list:
        print(error)

def main():

    # @dev: Target must be an ISO 639-1 language code.
    # See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    # """
    existing_languages = ["it", "fr", "tr", "bg", "ru", "fa", "vi", "es","pt","id","zh","ja"]
    multi_process_batch_translate_vtt_folder('courses', existing_languages)

if __name__ == '__main__':
    main()
