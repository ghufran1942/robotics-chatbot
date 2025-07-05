import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuration
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./vectorstore")
MAX_DOCUMENTS_PER_TOPIC = int(os.getenv("MAX_DOCUMENTS_PER_TOPIC", "50"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Robotics-related sources
ROBOTICS_SOURCES = {
    "ros_docs": "https://docs.ros.org/",
    "ros_wiki": "https://wiki.ros.org/",
    "stack_exchange": "https://robotics.stackexchange.com/",
    "arxiv": "https://arxiv.org/search/?query=robotics&searchtype=all&source=header"
}

# Common robotics topics for auto-generation
# COMMON_ROBOTICS_TOPICS = [
#     "PID controller",
#     "SLAM",
#     "robotic grippers", 
#     "localization",
#     "path planning",
#     "computer vision",
#     "sensor fusion",
#     "kinematics",
#     "dynamics",
#     "control systems",
#     "machine learning in robotics",
#     "autonomous navigation",
#     "manipulation",
#     "human-robot interaction"
# ] 