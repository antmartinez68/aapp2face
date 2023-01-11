import os

module_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(module_dir)

TEST_RESPONSES_PATH = f"{parent_dir}/aapp2face/cli/resources/sim-responses"
