import requests
import os

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

# GitHub GraphQL API
URL = "https://api.github.com/graphql"

query = """
query($login: String!) {
  user(login: $login) {
    pinnedItems(first: 6, types: REPOSITORY) {
      edges {
        node {
          ... on Repository {
            name
            url
            description
            stargazerCount
            forkCount
          }
        }
      }
    }
  }
}
"""

response = requests.post(
    URL,
    json={"query": query, "variables": {"login": USERNAME}},
    headers={"Authorization": f"Bearer {TOKEN}"}
)

data = response.json()
pinned = data["data"]["user"]["pinnedItems"]["edges"]

# Generate markdown
project_md = ""
for item in pinned:
    repo = item["node"]
    name = repo["name"]
    url = repo["url"]
    stars = repo["stargazerCount"]
    forks = repo["forkCount"]
    desc = repo["description"] or ""
    project_md += f"- [{name}]({url}) ⭐ {stars} 🍴 {forks} — {desc}\n"

# Read README
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

start_marker = "<!--START_SECTION:projects-->"
end_marker = "<!--END_SECTION:projects-->"
start_index = readme.find(start_marker) + len(start_marker)
end_index = readme.find(end_marker)

new_readme = readme[:start_index] + "\n" + project_md + readme[end_index:]

# Write back
with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)

# Commit & push
os.system('git config user.name "github-actions[bot]"')
os.system('git config user.email "[email protected]"')
os.system("git add README.md")
os.system('git commit -m "chore: update Projects section" || exit 0')
os.system("git push")
