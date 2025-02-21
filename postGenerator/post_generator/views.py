import asyncio
import os
import json
import requests
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from crawl4ai import AsyncWebCrawler
from django.conf import settings
# Initialize LLM Model (Groq Llama 3.1 70B)
GROQ_API_KEY = settings.GROQ_API_KEY  # Replace with your actual API key
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

# --- Prompt Templates ---
readme_prompt_template = PromptTemplate(
    input_variables=["title", "description", "features", "tech_stack"],
    template="""
    You are an AI that generates **well-structured README.md** files.

    **Project Title:** {title}
    **Description:** {description}
    
    **Key Features:**
    {features}

    **Tech Stack Used:**
    {tech_stack}

    Generate a professional **Markdown README** with:
    - Clear project introduction
    - Features list
    - Tech stack
    - Installation guide
    - Usage instructions
    - Contribution guidelines
    - License
    - Contact information

    Output:
    """
)

edit_prompt_template = PromptTemplate(
    input_variables=["existing_readme", "changes"],
    template="""
    You are an AI that **modifies** README.md files based on user feedback.

    **Current README.md:**
    {existing_readme}

    **Requested Changes:**
    {changes}

    Update the README accordingly while keeping a professional format.

    Output:
    """
)

linkedin_prompt_template = PromptTemplate(
    input_variables=["title", "description", "features", "tech_stack", "github_link", "deployment_link"],
    template="""
    You are a professional LinkedIn post writer.

    **Example of a well-structured LinkedIn post:**
    
    ---
    
    🚀 Excited to share my latest project with you all! 🎉  
    **Introducing: The LinkedIn Post Generator!**  

    This innovative tool helps users create LinkedIn posts from their GitHub README.md file or by providing custom input.  
    The best part? It automates the process using the LinkedIn API, making content sharing effortless! 💡  

    ✨ **Key Features:**  
    - Generate LinkedIn posts from a GitHub README.md file  
    - AI-powered content customization  
    - Direct LinkedIn API integration for automatic posting  
    - Supports multiple post formats (text, images, videos)  
    - User-friendly interface with minimal setup  

    🔧 **Tech Stack Used:** Python, Django, LinkedIn API, PostgreSQL, React  

    🔗 **Want to learn more? Check it out here:**  
    - GitHub: https://github.com/example/linkedin-post-generator  
    - Live Demo: https://linkedinpost.demo  

    Let's connect and explore the possibilities! 🚀🔥  
   
    ---

    **Now, generate a similar engaging LinkedIn post using the following extracted details, make sure you explain each and every functionality, DONT BOLD ANYTHING: (NO PREMABLE)**  

    🎉 **Introducing: {title}!**  

    🚀 **What it's about:**  
    {description}

    💡 **Key Features:**  
    {features}

    🔧 **Tech Stack Used:**  
    {tech_stack}

    🔗 **Check it out here:**  
    - GitHub: {github_link}  
    - Deployment: {deployment_link}

    Ensure the tone is **engaging, enthusiastic, and professional.**
    """
)


# def extract_json(text):
#     """Extracts valid JSON from a response by removing extra text before and after."""
#     match = re.search(r'\{.*\}', text, re.DOTALL)
#     if match:
#         json_str = match.group(0)
#         try:
#             return json.loads(json_str)
#         except json.JSONDecodeError:
#             return {"error": "Failed to parse extracted JSON.", "raw_response": json_str}
#     return {"error": "No valid JSON found in response.", "raw_response": text}

import re

def remove_preamble(text):
    """Removes the preamble 'Here is the generated README file:' from the text."""
    return re.sub(r"^Here is the generated README file:\s*\n+", "", text)


async def fetch_readme(url):
    """Scrape README.md content from GitHub."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        return result.markdown  # Extract the Markdown content

# --- API Views ---

#working
@csrf_exempt
async def generate_readme(request):
    """Generate a README.md file from user input."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        title = data.get("title")
        description = data.get("description")
        features = data.get("features", [])
        tech_stack = data.get("tech_stack", [])

        if not title or not description:
            return JsonResponse({"error": "Title and Description are required"}, status=400)

        formatted_prompt = readme_prompt_template.format(
            title=title,
            description=description,
            features="\n".join(features),
            tech_stack=", ".join(tech_stack),
        )

        messages = [
            SystemMessage(content="You are a professional README.md generator."),
            HumanMessage(content=formatted_prompt)
        ]

        response = await asyncio.to_thread(llm.invoke, messages)
        readme_content = remove_preamble(response.content)

        return JsonResponse({"readme": readme_content}, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

#need database
@csrf_exempt
async def edit_readme(request):
    """Edit an existing README.md file based on user input."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        existing_readme = data.get("existing_readme")
        changes = data.get("changes")

        if not existing_readme or not changes:
            return JsonResponse({"error": "Existing README and changes are required"}, status=400)

        formatted_prompt = edit_prompt_template.format(existing_readme=existing_readme, changes=changes)

        messages = [
            SystemMessage(content="You are an AI that edits README.md files professionally."),
            HumanMessage(content=formatted_prompt)
        ]

        response = await asyncio.to_thread(llm.invoke, messages)
        updated_readme = response.content

        return JsonResponse({"updated_readme": updated_readme}, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

# needs database
@csrf_exempt
async def view_readme(request):
    """Retrieve the stored README.md content."""
    if not os.path.exists("README.md"):
        return JsonResponse({"error": "README.md not found"}, status=404)

    with open("README.md", "r", encoding="utf-8") as file:
        content = file.read()

    return JsonResponse({"readme": content})

#working
@csrf_exempt
async def scrape_readme(request):
    """Scrape README from a GitHub URL and process it into a structured format."""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    try:
        data = json.loads(request.body)
        url = data.get("url")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    if not url:
        return JsonResponse({"error": "URL is required"}, status=400)

    # Scrape the README content from the provided URL
    readme_text = await fetch_readme(url)

    if not readme_text:
        return JsonResponse({"error": "Failed to fetch README from the provided URL"}, status=400)

    # Generate a well-structured README using Llama 3.1
    formatted_prompt = readme_prompt_template.format(
        title="Extracted from repository",
        description=readme_text,  # Use first 300 characters as description
        features="- Extracted features from the README",
        tech_stack="Extracted tech stack if available"
    )

    messages = [
        SystemMessage(content="You are a professional README.md generator."),
        HumanMessage(content=formatted_prompt)
    ]

    response = await asyncio.to_thread(llm.invoke, messages)
    structured_readme = remove_preamble(response.content)

    return JsonResponse({
        "original_readme": readme_text,
        "structured_readme": structured_readme
    }, safe=False)

# working
@csrf_exempt
async def generate_linkedin_post(request):
    """Generate a LinkedIn post and return extracted details."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        content = data.get("content")
        github_link = data.get("github_link", "Not provided")
        deployment_link = data.get("deployment_link", "Not provided")

        if not content:
            return JsonResponse({"error": "Content is required"}, status=400)

        # Step 1: AI extracts project details from content
        extract_prompt = f"""
        Extract the following details from the given content:
        - Project Title
        - Short Description
        - Key Features (as bullet points)
        - Tech Stack (as comma-separated values)

        Content: {content}

        Provide the extracted details in a structured JSON format:
        {{
            "title": "Extracted project title",
            "description": "Extracted project description",
            "features": ["Feature 1", "Feature 2", "Feature 3"],
            "tech_stack": ["Tech 1", "Tech 2", "Tech 3"]
        }}
        """

        messages = [SystemMessage(content="You are a structured data extractor."), HumanMessage(content=extract_prompt)]
        extract_response = await asyncio.to_thread(llm.invoke, messages)

        # DEBUG: Log raw response for debugging extraction issues
        print("Raw Extraction Response:", extract_response.content)

        # Step 2: Extract valid JSON from AI response
        try:
            extracted_data = json.loads(extract_response.content)
        except json.JSONDecodeError:
            json_match = re.search(r'```(?:json)?\n(.*?)\n```', extract_response.content, re.DOTALL)
            extracted_json = json_match.group(1) if json_match else extract_response.content.strip()
            try:
                extracted_data = json.loads(extracted_json)
            except json.JSONDecodeError:
                return JsonResponse({
                    "error": "Failed to extract details. Ensure content is clear.",
                    "raw_response": extract_response.content  # Debugging help
                }, status=400)

        # Step 3: Generate LinkedIn post using extracted details
        formatted_prompt = linkedin_prompt_template.format(
            title=extracted_data.get("title", "Unknown Project"),
            description=extracted_data.get("description", "No description available."),
            features="\n".join(extracted_data.get("features", ["No features listed."])),
            tech_stack=", ".join(extracted_data.get("tech_stack", ["Unknown tech stack"])),
            github_link=github_link,
            deployment_link=deployment_link
        )

        messages = [SystemMessage(content="You are a professional LinkedIn post generator."), HumanMessage(content=formatted_prompt)]
        response = await asyncio.to_thread(llm.invoke, messages)

        # Step 4: Extract the LinkedIn post safely
        raw_post = response.content.strip()

        # Fix: Start extracting text after the first `:`
        if ":" in raw_post:
            raw_post = raw_post.split(":", 1)[1].strip()

        # Step 5: Return everything in JSON
        return JsonResponse({
            "extracted_data": extracted_data,  # Extracted project details
            "linkedin_post": raw_post  # Final LinkedIn post (starting after `:`)
        }, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)




# --- LinkedIn Automation ---
ACCESS_TOKEN = settings.ACCESS_TOKEN

class LinkedinAutomate:
    def __init__(self, access_token, content):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        self.content = content
        self.user_id = self.get_user_id()

    def get_user_id(self):
        """Fetches the LinkedIn user ID."""
        url = "https://api.linkedin.com/v2/userinfo"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("sub")
        except requests.exceptions.RequestException:
            return None

    def prepare_payload(self):
        """Creates the LinkedIn post payload."""
        if not self.user_id:
            return None

        return json.dumps({
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": self.content},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        })

    def post_to_linkedin(self):
        """Sends a post to LinkedIn."""
        url = "https://api.linkedin.com/v2/ugcPosts"
        payload = self.prepare_payload()
        if not payload:
            return None

        try:
            response = requests.post(url, headers=self.headers, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

#working
@csrf_exempt
def post_on_linkedin(request):
    """Django API to post content on LinkedIn."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        linkedin_post = data.get("linkedin_post")
        if not linkedin_post:
            return JsonResponse({"error": "LinkedIn post content is required"}, status=400)

        linkedin_bot = LinkedinAutomate(ACCESS_TOKEN, linkedin_post)
        response = linkedin_bot.post_to_linkedin()

        return JsonResponse({"message": "Post successful", "linkedin_response": response} if response else {"error": "Failed to post on LinkedIn"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
