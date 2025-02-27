# Script - generate JSONL

![ahastudioLogo](https://github.com/user-attachments/assets/51f405c7-a81a-4dd7-af14-973b3521aea2)

**Author**: [Junior Sacarias](https://github.com/juniorSacarias)

---

## 📖 Introduction

This repository was born from the need to obtain, during the research carried out on training the artificial intelligence llama2, fast data conversions to the format necessary for this purpose.

---

## ⚙️ Configuration

  To configure these scripts you need to clearly differentiate their purposes:
  
  1. Convert.py
     is a console app created in python3 which allows us to easily perform predefined actions.

     First, it will ask us for the path within our project for the folder containing the pdfs, second, it will ask us if the cvs files are in the same folder as the pdfs, this only applies if we will use the client to process cvs, the recommendation is that you separate the cvs from the training pdfs. Third, it will ask us for the path where we want to obtain the different conversion results.

     After this brief configuration, it will give us access to the client.

     ![image](https://github.com/user-attachments/assets/97f7bd75-1c7a-4df4-b122-566170df6962)

  2. Monitory.py
     is designed to be a computing resource monitoring script. This means that if we launch it locally it will record the use of our resources.

     In the first instance it is designed to be launched in the background within a Google Colab or Jupiter notebook.
      
     Its configuration is very simple:
     
     First we will need to upload this file to the storage of the notebook we are using under the name monitory.py
     
     Second we will use this line of code to install the dependencies:
     
     !pip install GPUtil psutil
     
     Third step we will launch the script in the background:

     !nohup python monitory.py &
      
     With this configuration we will obtain two files: one with the extension .csv and another with the extension .log

## 👨‍🔧 Start the convertions

  In this section we will explain the use of the tools introduced within the client (it is important that it is updated as new features are added)

1. Summarize PDFs and generate questions,
  By selecting this option using the number 1 the script will ask the user to enter the number of unique questions they want to receive, once the number is entered the script will start to iterate over the training folder that we have determined.
  it will extract the file, summarize it using the llama2 model served in ollama locally (when using ollama to serve the model we must take into account the waiting time between response and response) once the summary is generated the questions will start to be generated and once the questions are finished it will start to solve them returning three files in the configured results folder:
  summary.txt, questions.txt and a .jsonl file
   ![image](https://github.com/user-attachments/assets/5a42596a-b3ff-4e7e-b3ee-e42d38108a80)

2. Process all CVs in the folder
   By selecting this option using the number 2 the script will ask the user to enter the number of unique questions they want to receive, once the number is entered the script will start to iterate over the cvs folder that we have determined.
   it will extract the file, if the file does not contain enough content in text format it will use OCR to be able to view the information and generate the summary, it will summarize it using the llama2 model served in ollama locally (when using ollama to serve the model we must take into account the waiting time between response and response) once the summary is generated the questions will begin to be generated and once the questions are finished it will begin to solve them returning three files in the configured results folder:
   summary.txt, questions.txt and a .jsonl file
   ![image](https://github.com/user-attachments/assets/3320db17-4ba5-455f-9153-d74700147f90)
