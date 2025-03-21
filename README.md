# **Boolean Search Engine (ShahQuery)**  

![image](https://github.com/user-attachments/assets/8bd6e99f-439b-4543-9c59-e10fb3f5406b)


This project implements a **Boolean & Positional Search Engine** using Python (Flask), React, and NLP techniques. It allows users to query documents using **Boolean expressions** (`AND`, `OR`, `NOT`) and **proximity search** (words within a given distance).  

## **Features**  

✅ **Boolean Search** (`AND`, `OR`, `NOT`)  
✅ **Positional Search** (`word1 word2 /k`)  
✅ **Search Suggestions** (Auto-complete)  
✅ **Document Snippets** (Highlighted terms)  
✅ **Full Document View**  
✅ **Fast Query Processing**  

---

## **Tech Stack**  

🔹 **Backend**: Python (Flask), NLTK, JSON  
🔹 **Frontend**: React, Axios, Framer Motion  
🔹 **Data Storage**: JSON-based Inverted & Positional Index  

---

![image](https://github.com/user-attachments/assets/e015b98c-2555-4467-b5e7-f06d56e0db13)


## **How It Works**  

1. **Indexing (`indexer.py`)**  
   - Reads text files from the `/documents` folder  
   - Tokenizes and stems words (optional)  
   - Builds an **inverted index** (word → documents)  
   - Builds a **positional index** (word → document → positions)  
   - Saves indexes as JSON  

2. **Search (`Main.py`)**  
   - Loads indexes  
   - Supports **Boolean search** (`AND`, `OR`, `NOT`)  
   - Supports **Positional search** (`word1 word2 /k`)
   - Supports **Exact phrase search** ("Machine Learning")
   - Returns relevant documents & snippets  

3. **Frontend (`App.js`)**  
   - Input field for search queries  
   - Fetches **search suggestions**  
   - Displays **results & snippets**  
   - Opens full document in a modal  

---

## **Setup & Installation**  

### **Backend Setup (Python)**  

1️⃣ Install dependencies:  
```bash
pip install -r requirements.txt
```  

2️⃣ Run the indexer: (Index files are already there, so no need for this)
```bash
python indexer.py
```  

3️⃣ Start the Flask server:  
```bash
python Main.py
```  

Server runs at: **`http://127.0.0.1:8000`**  

---

### **Frontend Setup (React)**  

1️⃣ Install dependencies:  
```bash
npm install
```  

2️⃣ Start the React app:  
```bash
npm start
```  

Frontend runs at: **`http://localhost:3000`**  

---

## **API Endpoints**  

###  **Search API**  
**`GET /search?query=<query>`**  
- Performs Boolean or Positional search  
- Returns document IDs and snippets

![image](https://github.com/user-attachments/assets/80d7db83-2d1d-41de-9474-f4e51f36144b)


###  **Suggestions API**  
**`GET /suggest?query=<query>`**  
- Returns autocomplete suggestions
  
![image](https://github.com/user-attachments/assets/ab9a8fd1-dd0d-4a47-86a7-84d28fdafb88)


###  **Full Document API**  
**`GET /document?doc_id=<id>`**  
- Fetches full document content
  
![image](https://github.com/user-attachments/assets/3400ebaf-d5ab-4444-8a84-6b5195bb79c2)

###  **Exact Query Search**

![image](https://github.com/user-attachments/assets/b72e66d5-6090-48d0-be5d-b8b32ea721c3)


---

## **Contributor**  
👨‍💻 **Shahzain Zaidi**  

Happy Coding! 🚀
