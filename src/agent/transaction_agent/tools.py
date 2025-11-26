from langchain_core.tools import tool

@tool
def extra_data():
    """This is additional data on who Adegbite David is"""

    return "He is a back-end developer"