from app.builders.project_builder import ProjectBuilder


def main():

    print("=" * 60)
    print("AUTODEV AI - PROJECT BUILDER TEST")
    print("=" * 60)

    builder = ProjectBuilder()

    llm_output = """
FILE: app.py

def add(a, b):
    return a + b


if __name__ == "__main__":
    print(add(10, 20))


FILE: README.md

# Calculator

Simple Python calculator project.


FILE: requirements.txt

"""


    print("\nBuilding project...\n")

    result = builder.build(
        project_name="Calculator Test",
        llm_output=llm_output,
    )

    print("=" * 60)
    print("BUILD RESULT")
    print("=" * 60)

    print(f"Project path: {result['project_path']}")
    print(f"ZIP path: {result['zip_path']}")
    print(f"File count: {result['file_count']}")

    print("\nFiles:")

    for file in result["files"]:
        print(f"  - {file}")

    print("\n" + "=" * 60)
    print("PROJECT BUILDER TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()