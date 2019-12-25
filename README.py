import os
import urllib.parse

directories = sorted(
    d for d in os.listdir(".") if os.path.isdir(d) and not d.startswith(".")
)


for d in directories:

    def make_column(subdir_name, file_name="notebook.ipynb"):
        path = os.path.join(d, subdir_name, file_name)
        if os.path.exists(path):
            return f"[{subdir_name}]({urllib.parse.quote(path)})"
        else:
            return ""

    print(
        f"|{d.replace(' - ', '|')}|{make_column('Starter')}|{make_column('Submission')}|{make_column('Solution')}"
    )
