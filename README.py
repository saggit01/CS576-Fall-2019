import os
import urllib.parse

directories = sorted(
    d for d in os.listdir(".") if os.path.isdir(d) and not d.startswith(".")
)

for d in directories:
    url = urllib.parse.quote(d)
    solution_url = f"{url}/Solution"
    starter_url = (
        f"{url}/Starter"
        if os.path.exists(os.path.join(d, "Starter"))
        else f"{url}/Startercode"
    )
    submission_url = f"{url}/Submission"

    print(
        f"|{d}|[Starter Code]({starter_url})|[Submission]({submission_url})|[Solution]({solution_url})"
    )
