#Hello, you're all welcome to today's python class
#So at the end of today's lesson, you will be able to :
#Understand how to read/write from and to files with python , use 'with open(...)' safely for file operations, differenciate between text and binary files 
#Read and write json data using the json module, read and write CSV files using the csv module
#Build a mini project to practice what we've learnt 
#Thank you 

#But first off, we're stating with a little recap of last week's lessons

#1. File reading + Writing Basics 
#Explanation of the concept of files....long term storage, etc
#Modes of files handling in python : r, w, a, b
#using 'with open(...) as f' 
import os

with open("hello.txt", "w") as f:
    f.write("Hello, we are learning how to use file handling modes in python!")

with open("hello.txt", "a") as f:
    f.write("We are all students and we're currently in B3")

with open("hello.xls", "w") as f:
    f.write("this is a random text")

with open("hello.txt", "r") as f:
    c = f.read()
    print(c) 

with open("hello.txt", "a") as f:
    f.write("This is an appended version")
print("File saved at:", os.path.abspath("hello.txt"))


#Now you guys should also create a little word file with your full name and favorite programming language 

#Now we move to the next thing...the text/binary files
#What's binary? When you hear binary what's comes to mind?
#So then what's the difference between a normal text file and a binary file?

"""
3. Text vs Binary Files (10 mins)
🧊 Concept:

Text = readable (e.g. .txt)

Binary = not directly human-readable (e.g. .jpg, .exe)

🧪 Demo:

Read a .txt file and a .jpg file in binary mode

4. Working with JSON (20 mins)
📘 Explain:

JSON = JavaScript Object Notation (used for APIs, configs)

📌 Example:

python
Copy
Edit
import json

data = {"name": "Alice", "age": 22}
with open("data.json", "w") as f:
    json.dump(data, f)

with open("data.json", "r") as f:
    print(json.load(f))
💡 Mini-Project Idea:

"Student Database" – Save student name and age in a JSON file

5. Working with CSV (20 mins)
📘 Explain:

CSV = Comma-Separated Values (used in spreadsheets)

📌 Example:

python
Copy
Edit
import csv

with open("marks.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Score"])
    writer.writerow(["John", 90])
    writer.writerow(["Jane", 95])
💬 Activity:

Create a CSV file that stores your classmates' names and scores

6. Hands-On Group Challenge (15 mins)
🚀 Challenge:

“Build a simple program that lets a user enter their name and age, saves it to a JSON file, and then shows all stored users.”

🏆 You can make it competitive:

Best code

Most creative formatting

Least bugs

7. Recap + Q&A (5 mins)
Review:

File modes

JSON vs CSV

with open safety





JSON (JavaScript Object Notation) is a lightweight format used to store and exchange data — like a .txt file that holds structured data.

Example:

json
Copy
Edit
{
  "name": "Alice",
  "age": 25,
  "hobbies": ["coding", "reading"]
}
It maps perfectly to Python dictionaries, making it easy to use!

🔧 Python’s json Module
Python has a built-in module called json for handling JSON files.

python
Copy
Edit
import json
🟢 1. Reading JSON from a File
python
Copy
Edit
import json

with open("data.json", "r") as f:
    data = json.load(f)  # Converts JSON into Python dictionary
    print(data)
Example data.json:

json
Copy
Edit
{
  "name": "John",
  "age": 30,
  "skills": ["Python", "C++"]
}
🔁 json.load() = file → Python dictionary

🔵 2. Writing JSON to a File
python
Copy
Edit
import json

data = {
    "name": "Jane",
    "age": 22,
    "skills": ["JavaScript", "HTML"]
}

with open("output.json", "w") as f:
    json.dump(data, f, indent=4)
🔁 json.dump() = Python dictionary → file
indent=4 makes it pretty (readable).

🟠 3. Working with JSON Strings
➤ Convert from JSON string to Python object:
python
Copy
Edit
json_str = '{"name": "Mary", "age": 28}'
data = json.loads(json_str)
print(data["name"])  # Mary
➤ Convert Python object to JSON string:
python
Copy
Edit
import json

data = {"name": "Sam", "age": 21}
json_str = json.dumps(data, indent=2)
print(json_str)
json.loads() ← string → dict
json.dumps() ← dict → string

🧠 Summary Table
Action	Function
Read JSON from file	json.load()
Write JSON to file	json.dump()
JSON string → Python	json.loads()
Python → JSON string	json.dumps()

🧪 Quick Practice
Exercise:
Create a file student.json with this content:

json
Copy
Edit
{
  "name": "Alex",
  "level": "100",
  "course": ["Python", "C++"]
}
Then try this Python code:

python
Copy
Edit
import json

with open("student.json") as f:
    student = json.load(f)

print("Courses:", student["course"])

""" 


with open("test.png", "rb") as f:
    data = f.read()
   # print(data)

