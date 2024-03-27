# Video Subtitles Translator

The Video Subtitles Translator is a powerful tool designed to automate the translation of VTT subtitle files into multiple languages leveraging the Google Cloud Translation API. It streamlines the process of identifying untranslated files in a specified directory and employs multiprocessing to enhance the speed of translations.

## Features

- **Automatic Detection**: Identifies missing language translations for VTT files within a designated folder.
- **Google Cloud Integration**: Compatible with both Google Cloud Translation API versions 2 and 3.
- **Efficiency**: Utilizes multiprocessing for rapid batch processing of translations.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.x installed on your machine.
- An active Google Cloud Platform (GCP) account and a project set up with the following services enabled:
  - Google Translation API
  - Google Cloud Storage (Bucket)

## Getting Started

1. **Clone the Repository**
   
   Clone this repository to your local machine using the following command:
   ```bash
   git clone [Repository URL](https://github.com/Eversmile12/vtt-translator)
   ```
   
2. **Set Up a Virtual Environment**

   Navigate to the root directory of the cloned repository, then create and activate a virtual environment:
   ```
   python -m venv subtitles-translation && source subtitles-translation/bin/activate
   ```

3. **Install Dependencies**

   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download and Authenticate gcloud CLI**

   Download the [gcloud CLI tools](https://cloud.google.com/sdk/docs/install) suitable for your operating system. Then, authenticate your local environment with GCP:
   ```
   gcloud init && gcloud auth login
   ```
   This command opens a Google login window. Sign in with the account linked to your GCP project.

5. **Acquire Your GOOGLE BEARER Token**

   Obtain your Google Cloud access token by running:
   ```
   gcloud auth application-default print-access-token
   ```
   Copy this token for later use.

6. **Configure Environment Variables**

   Rename the `.env.template` file in the root directory of the project to `.env` and populate it with your GCP credentials and configurations:
   ```
   GOOGLE_BEARER=your-google-bearer
   PROJECT_ID=your-project-id
   PROJECT_LOCATION=your-project-location
   BUCKET_NAME=bucket-name
   ```
   You can find your project ID, location, and bucket name in the Google Cloud Console.

7. **Prepare Your Subtitles**

   Place your VTT files in the "courses" folder within the project directory.

8. **Run the Translation Script**

   To start the translation process, execute:
   ```bash
   python main.py
   ```

## Configuring Your Translations

### Glossaries

The tool includes predefined glossaries in the "glossaries" folder, allowing for customized translations. You can modify these files to adjust translations or add new terms.

To update glossaries in Google Cloud with your local changes, run:
```
python main.py -update
```

### Adding New Languages

To translate into additional languages, edit the `existing_languages` list in the `main` function of `main.py` to include new [ISO 639-1 language codes](https://gist.github.com/jrnk/8eb57b065ea0b098d571).

### Structure Support

The tool supports translating VTT files located directly within the "courses" folder or nested in subdirectories, maintaining the original folder structure in the output.

## Customization

To add more languages for translation, modify the `existing_languages` variable in the `main.py` file, following the ISO 639-1 standards.

## Support

For detailed information about the Google Cloud Translation API, including supported languages and API reference, visit the [Google Cloud Translation documentation](https://cloud.google.com/translate/docs/reference/rest#supported_languages).

Should you encounter any issues or have questions, this documentation is a comprehensive resource for troubleshooting and learning more about the capabilities of the Google Cloud Translation API.
