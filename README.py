import os
import urllib.parse

directories = sorted(
    d for d in os.listdir(".") if os.path.isdir(d) and not d.startswith(".")
)

for d in directories:
    url = urllib.parse.quote(d)
    print(f"""|{d}||""")
