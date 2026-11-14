"""The OCR H446 specification: two papers, eight sections and twenty-four sub-topics."""

from app.services.seed_data.types import SeedSection, SeedTopic

SECTIONS: tuple[SeedSection, ...] = (
    # --- Paper 1: Computer Systems ---------------------------------------------------------
    SeedSection(
        paper=1,
        code="1.1",
        name="The characteristics of contemporary processors, input, output and storage devices",
        topics=(
            SeedTopic(
                "1.1.1",
                "Structure and function of the processor",
                (
                    "CPU Components and Registers",
                    "CPU Buses",
                    "The Fetch-Decode-Execute Cycle",
                ),
            ),
            SeedTopic(
                "1.1.2",
                "Types of processor",
                (
                    "CISC and RISC Processors",
                    "GPUs and their Uses",
                    "Multicore and Parallel Systems",
                ),
            ),
            SeedTopic(
                "1.1.3",
                "Input, output and storage",
                (
                    "Input, Output and Storage Devices",
                    "Magnetic, Flash and Optical Storage",
                    "RAM and ROM",
                ),
            ),
        ),
    ),
    SeedSection(
        paper=1,
        code="1.2",
        name="Software and software development",
        topics=(
            SeedTopic(
                "1.2.1",
                "Systems Software",
                (
                    "Function and Purpose of Operating Systems",
                    "Memory Management",
                    "Interrupts",
                ),
            ),
            SeedTopic(
                "1.2.2",
                "Applications Generation",
                (
                    "Nature of Applications",
                    "Utilities",
                    "Open Source and Closed Source Software",
                ),
            ),
            SeedTopic(
                "1.2.3",
                "Software Development",
                (
                    "Software Development Methodologies",
                    "Advantages and Disadvantages of Methodologies",
                    "Writing and Following Algorithms",
                ),
            ),
            SeedTopic(
                "1.2.4",
                "Types of Programming Language",
                (
                    "Programming Paradigms",
                    "Procedural Languages",
                    "Assembly Language and Little Man Computer",
                ),
            ),
        ),
    ),
    SeedSection(
        paper=1,
        code="1.3",
        name="Exchanging data",
        topics=(
            SeedTopic(
                "1.3.1",
                "Compression, Encryption and Hashing",
                (
                    "Lossy and Lossless Compression",
                    "Run Length Encoding and Dictionary Coding",
                    "Symmetric and Asymmetric Encryption",
                ),
            ),
            SeedTopic(
                "1.3.2",
                "Databases",
                (
                    "Flat File and Relational Databases",
                    "Primary, Foreign and Secondary Keys",
                    "Entity Relationship Modelling",
                ),
            ),
            SeedTopic(
                "1.3.3",
                "Networks",
                (
                    "Characteristics of Networks and Protocols",
                    "The TCP/IP Stack",
                    "DNS",
                ),
            ),
            SeedTopic(
                "1.3.4",
                "Web Technologies",
                ("HTML", "CSS", "JavaScript"),
            ),
        ),
    ),
    SeedSection(
        paper=1,
        code="1.4",
        name="Data types, data structures and algorithms",
        topics=(
            SeedTopic(
                "1.4.1",
                "Data Types",
                (
                    "Data Types",
                    "Binary and Denary Conversions",
                    "Sign and Magnitude and Two's Complement",
                ),
            ),
            SeedTopic(
                "1.4.2",
                "Data Structures",
                (
                    "Arrays, Records, Lists and Tuples",
                    "Linked Lists",
                    "Graphs",
                ),
            ),
            SeedTopic(
                "1.4.3",
                "Boolean Algebra",
                (
                    "Logic Gate Diagrams and Truth Tables",
                    "Simplifying Boolean Expressions",
                    "Karnaugh Maps",
                ),
            ),
        ),
    ),
    SeedSection(
        paper=1,
        code="1.5",
        name="Legal, moral, cultural and ethical issues",
        topics=(
            SeedTopic(
                "1.5.1",
                "Computing-related legislation",
                (
                    "The Data Protection Act",
                    "The Computer Misuse Act",
                    "The Copyright, Designs and Patents Act",
                ),
            ),
            SeedTopic(
                "1.5.2",
                "Moral and ethical issues",
                (
                    "Computers in the Workforce",
                    "Automated Decision Making",
                    "Artificial Intelligence",
                ),
            ),
        ),
    ),
    # --- Paper 2: Algorithms and Programming -----------------------------------------------
    SeedSection(
        paper=2,
        code="2.1",
        name="Elements of computational thinking",
        topics=(
            SeedTopic(
                "2.1.1",
                "Thinking abstractly",
                (
                    "The Nature of Abstraction",
                    "The Need for Abstraction",
                    "Abstraction and Reality",
                ),
            ),
            SeedTopic(
                "2.1.2",
                "Thinking ahead",
                (
                    "Inputs and Outputs",
                    "Preconditions",
                    "Caching and Reusable Components",
                ),
            ),
            SeedTopic(
                "2.1.3",
                "Thinking procedurally",
                (
                    "Identifying the Components of a Problem",
                    "Identifying the Components of a Solution",
                    "Order of Steps and Sub-procedures",
                ),
            ),
            SeedTopic(
                "2.1.4",
                "Thinking logically",
                (
                    "Identifying Decision Points",
                    "Logical Conditions",
                    "Decisions and Program Flow",
                ),
            ),
            SeedTopic(
                "2.1.5",
                "Thinking concurrently",
                (
                    "Concurrent Processing",
                    "Benefits and Trade-offs of Concurrency",
                    "Identifying Concurrent Parts of a Problem",
                ),
            ),
        ),
    ),
    SeedSection(
        paper=2,
        code="2.2",
        name="Problem solving and programming",
        topics=(
            SeedTopic(
                "2.2.1",
                "Programming techniques",
                (
                    "Programming Constructs",
                    "Recursion",
                    "Global and Local Variables",
                ),
            ),
            SeedTopic(
                "2.2.2",
                "Computational methods",
                (
                    "Problem Decomposition",
                    "Divide and Conquer",
                    "Use of Abstraction",
                ),
            ),
        ),
    ),
    SeedSection(
        paper=2,
        code="2.3",
        name="Algorithms",
        topics=(
            SeedTopic(
                "2.3.1",
                "Algorithms",
                (
                    "Time and Space Complexity",
                    "Big O Notation",
                    "Algorithms for Stacks",
                ),
            ),
        ),
    ),
)

# Exam series with past papers, newest first.
EXAM_SERIES: tuple[str, ...] = (
    "June 2024",
    "June 2023",
    "June 2022",
    "November 2021",
    "November 2020",
    "June 2019",
    "June 2018",
    "June 2017",
    "Specimen",
)

# Static files served by the frontend from frontend/public/resources/.
WORKSHEET_URL = "/resources/worksheets/sample-worksheet.pdf"
NOTES_URL = "/resources/notes/sample-notes.pdf"
EXAM_PACK_URL = "/resources/exam-packs/sample-exam-pack.pdf"
PAST_PAPER_URL = "/resources/past-papers/sample-past-paper.pdf"
WALKTHROUGH_URL = (
    "https://www.youtube.com/results?search_query=OCR+H446+Computer+Science+Past+Paper"
)

WORKSHEETS_PER_TOPIC = 3
NOTES_PER_TOPIC = 2
EXAM_PACKS_PER_SECTION = 2
