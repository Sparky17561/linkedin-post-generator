import asyncio
import json
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage, HumanMessage

# Initialize Groq API key
GROQ_API_KEY = "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"  # Replace with your actual API key

# Initialize LLM Model (Groq Llama 3.1 70B)
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

# Prompt Template for README.md generation
readme_prompt_template = PromptTemplate(
    input_variables=["project_description"],
    template="""
    You are an AI that generates **well-structured README.md** files.

    Based on the following project details, create a **professional** and **detailed** `README.md` file with:
    
    - A project title
    - A brief but **clear description** of the project
    - A structured installation guide
    - A usage guide explaining how to use the project
    - A list of key features
    - A "Tech Stack" section listing technologies used
    - A "Contributing" section with guidelines
    - A "License" section
    - A "Contact" section with placeholders for GitHub & email

    **Project Details Provided by User:**
    {project_description}

    Ensure the README follows **Markdown syntax** and is **formatted professionally**.
    Start directly with the README content without extra explanation.

    Output:
    """
)

async def generate_readme(project_description):
    """Generate a README.md file using Groq Llama 3.1 based on user input."""
    
    # Format the prompt
    formatted_prompt = readme_prompt_template.format(project_description=project_description)
    
    # Send the request to Llama 3.1
    messages = [
        SystemMessage(content="You are a professional README.md generator."),
        HumanMessage(content=formatted_prompt)
    ]

    response = llm.invoke(messages)
    
    # Extract and save the README.md content
    readme_content = response.content

    with open("README.md", "w", encoding="utf-8") as file:
        file.write(readme_content)

    return readme_content

async def main():
    """Main function to take user input and generate README.md."""
    print("\n📝 Welcome to the README.md Generator!\n")
    project_description = input("Describe your project (features, tech stack, purpose, etc.):\n\n")
    
    print("\n🚀 Generating README.md...\n")
    readme_content = await generate_readme(project_description)
    
    print("\n✅ README.md generated successfully!\n")
    print("📄 Preview:\n")
    print(readme_content)
    print("\n💾 The file has been saved as README.md in your current directory.")

if __name__ == "__main__":
    asyncio.run(main())
