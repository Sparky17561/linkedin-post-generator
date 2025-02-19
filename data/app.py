import asyncio
import os
import json
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage, HumanMessage

# Initialize Groq API key
GROQ_API_KEY = "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"  # Replace with your actual API key

# Initialize LLM Model (Groq Llama 3.1 70B)
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

# Prompt Template for generating README.md
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

# Prompt Template for editing README.md
edit_prompt_template = PromptTemplate(
    input_variables=["existing_readme", "changes"],
    template="""
    You are an AI that **modifies** README.md files based on user feedback.

    Given the following existing README file:

    **Current README.md:**
    ----------------------
    {existing_readme}

    The user wants the following changes:
    --------------------------------------
    {changes}

    Please update the README file **while preserving the original structure** and apply the necessary changes.

    Ensure the updated README remains **well-structured** and **properly formatted**.

    Output:
    """
)

async def generate_readme():
    """Generate a README.md file from scratch."""
    project_description = input("\nDescribe your project (features, tech stack, purpose, etc.):\n\n")
    
    print("\n🚀 Generating README.md...\n")
    formatted_prompt = readme_prompt_template.format(project_description=project_description)

    messages = [
        SystemMessage(content="You are a professional README.md generator."),
        HumanMessage(content=formatted_prompt)
    ]

    response = llm.invoke(messages)
    readme_content = response.content

    with open("README.md", "w", encoding="utf-8") as file:
        file.write(readme_content)

    print("\n✅ README.md has been created successfully!\n")
    print("📄 Preview:\n")
    print(readme_content)

async def edit_readme():
    """Edit an existing README.md file based on user input."""
    if not os.path.exists("README.md"):
        print("\n⚠️ No README.md file found in the current directory. Generate one first!\n")
        return

    with open("README.md", "r", encoding="utf-8") as file:
        existing_readme = file.read()

    print("\n📄 Current README.md content:\n")
    print(existing_readme)
    
    changes = input("\nWhat changes would you like to make to the README?\n\n")

    print("\n✍️ Applying changes...\n")
    formatted_prompt = edit_prompt_template.format(existing_readme=existing_readme, changes=changes)

    messages = [
        SystemMessage(content="You are an AI that edits README.md files professionally."),
        HumanMessage(content=formatted_prompt)
    ]

    response = llm.invoke(messages)
    updated_readme = response.content

    with open("README.md", "w", encoding="utf-8") as file:
        file.write(updated_readme)

    print("\n✅ README.md has been updated successfully!\n")
    print("📄 Updated Preview:\n")
    print(updated_readme)

async def main():
    """Main function to provide user options."""
    while True:
        print("\n📝 README.md Generator & Editor")
        print("1️⃣ Generate a new README.md")
        print("2️⃣ Edit an existing README.md")
        print("3️⃣ Exit")
        
        choice = input("\nChoose an option (1, 2, or 3): ")

        if choice == "1":
            await generate_readme()
        elif choice == "2":
            await edit_readme()
        elif choice == "3":
            print("\n👋 Exiting... Goodbye!\n")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    asyncio.run(main())
