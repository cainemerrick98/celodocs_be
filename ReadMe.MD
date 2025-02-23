# CeloDocs API

A personal project for my team at work. 

An API that can receive queries about the celonis platform, find the relevant information in the product documentation and pass this information through an LLM to give the user an answer to the query. 

Essentially its a RAG pipeline for my teams technical product documentation

I plan to deploy the API and provide a borwser extension interface to interact with the product - for now you can just run it locally.

# To Run Locally

1. Clone the repository
    ```
    git clone https://github.com/yourusername/celodocs.git
    ```

2. Create a virtual environment
    ```
    python -m venv venv
    ```

3. Install the dependencies
    ```
    pip install -r requirements.txt
    ```

4. Create a .env file in the root directory and add your API key
    ```
    PROD_KEY=your_api_key
    ```

4. Run the script - this will scrape the documentation, extract the documents and create the embeddings
    ```
    python celodocs/scripts/workflow.py
    ```

5. Run the Command Line API
    ```
    python celodocs/query_api.py
    ```


