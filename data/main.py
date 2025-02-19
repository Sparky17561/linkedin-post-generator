import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage, HumanMessage

# Initialize Groq API key
GROQ_API_KEY = "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"  # Replace with your actual API key

# Initialize LLM Model (Groq Llama 3.1 70B)
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

# Define a structured PromptTemplate for README extraction
readme_prompt_template = PromptTemplate(
    input_variables=["readme_text"],
    template="""
    NO PREMABLE
    You are an AI that extracts structured JSON from GitHub README files. 
    Given the following README content, extract the key sections and return a JSON object with:
    
    - `title`: The project title
    - `description`: A short project description
    - `features`: Any key features (if available)

    Ensure the output is **valid JSON** with properly formatted keys.

    README Content:
    -----------------
    {readme_text}

    Output JSON:
    """
)

# Define a PromptTemplate for LinkedIn post generation
linkedin_prompt_template = PromptTemplate(
    input_variables=["title", "description", "features", "github_link", "deployment_link", "tech_stack", "user_prompt"],
    template="""
    NO PREMABLE or BOILERPLATE
    You are an AI that generates professional LinkedIn posts for project announcements.

    Write a **first-person** LinkedIn post based on the details below:

    🎉 **Here’s my latest project: {title}!**  

    🚀 **What it's about:**  
    {description}

    💡 **Key Features:** explain in detail about each and every feature  
    {features}

    🔧 **Tech Stack Used:**  
    {tech_stack}

    🤖 **User Interaction Prompt:**  
    {user_prompt}

    🔗 **Check it out here:**  
    - GitHub: {github_link}  
    - Deployment: {deployment_link}

    Let's connect and discuss more! 🚀🔥  

    Ensure the post is **engaging, friendly, and concise**.
    
    Output:
    """
)

def extract_json(text):
    """Extracts valid JSON from a response by removing extra text before and after."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Failed to parse extracted JSON.", "raw_response": json_str}
    return {"error": "No valid JSON found in response.", "raw_response": text}

async def fetch_readme(url):
    """Scrape README.md content from GitHub."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        print(result.markdown)
        return result.markdown  # Extract the Markdown content

async def process_readme_with_groq(readme_text):
    """Use Groq Llama 3.1 to extract structured data from README and generate a LinkedIn post."""
    
    # Process README with structured prompt
    formatted_prompt = readme_prompt_template.format(readme_text=readme_text)
    
    messages = [
        SystemMessage(content="You are a structured data extraction assistant."),
        HumanMessage(content=formatted_prompt)
    ]

    response = llm.invoke(messages)
    readme_data = extract_json(response.content)

    if "error" in readme_data:
        return readme_data

    # Ask for missing inputs
    github_link = input("🔗 Enter the GitHub repository link: ")
    deployment_link = input("🌍 Enter the deployment link: ")
    tech_stack = input("⚙️ Enter the tech stack used: ")
    user_prompt = input("📝 Enter a brief user interaction prompt (e.g., how users interact with the project): ")

    # Generate LinkedIn post using extracted README data
    linkedin_prompt = linkedin_prompt_template.format(
        title=readme_data.get("title", "Unknown Project"),
        description=readme_data.get("description", "No description available."),
        features=", ".join(readme_data.get("features", ["Not specified"])),
        github_link=github_link,
        deployment_link=deployment_link,
        tech_stack=tech_stack,
        user_prompt=user_prompt
    )

    linkedin_messages = [
        SystemMessage(content="You are an AI that generates LinkedIn posts for projects."),
        HumanMessage(content=linkedin_prompt)
    ]

    linkedin_response = llm.invoke(linkedin_messages)

    return {
        "structured_data": readme_data,
        "linkedin_post": linkedin_response.content
    }

async def main():
    """Main function to scrape README and generate LinkedIn post."""
    url = input("📂 Enter the GitHub README URL: ")

    print("🔍 Scraping README.md...")
    readme_text = await fetch_readme(url)
    
    print("🤖 Processing with Llama 3.1 70B...")
    processed_data = await process_readme_with_groq(readme_text)
    
    if "error" in processed_data:
        print(f"⚠️ Error: {processed_data['error']}")
        print("Raw Response:\n", processed_data["raw_response"])
    else:
        print("\n📜 Extracted README (JSON Format):\n")
        print(json.dumps(processed_data["structured_data"], indent=2))

        print("\n💼 Generated LinkedIn Post:\n")
        print(processed_data["linkedin_post"])

        # Save the generated LinkedIn post to a file named post.txt
        with open("post.txt", "w", encoding="utf-8") as file:
            file.write(processed_data["linkedin_post"])
        print("\n✅ The LinkedIn post has been saved to post.txt")

if __name__ == "__main__":
    asyncio.run(main())
