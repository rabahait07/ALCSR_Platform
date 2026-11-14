"""Multiple-choice questions for Paper 1 (Computer Systems), keyed by specification code."""

from app.services.seed_data.types import SeedQuestion as Q

_LMC_ADD_PROGRAM = """\
        INP
        STA num
        INP
        ADD num
        OUT
        HLT
num     DAT"""

PAPER_1_QUESTIONS: dict[str, tuple[Q, ...]] = {
    # --- 1.1.1 Structure and function of the processor -------------------------------------
    "1.1.1": (
        Q(
            "Which register holds the address of the next instruction to be fetched?",
            (
                "Memory Address Register (MAR)",
                "Program Counter (PC)",
                "Current Instruction Register (CIR)",
                "Accumulator (ACC)",
            ),
            1,
            "The Program Counter always holds the address of the next instruction. At the "
            "start of the fetch stage its contents are copied to the MAR, and it is then "
            "incremented so that it points to the following instruction.",
        ),
        Q(
            "At the start of the fetch stage, the contents of the Program Counter are copied "
            "into which register?",
            (
                "Memory Data Register (MDR)",
                "Current Instruction Register (CIR)",
                "Accumulator (ACC)",
                "Memory Address Register (MAR)",
            ),
            3,
            "The address in the PC is copied to the MAR, which holds the address of the "
            "memory location about to be read. The instruction found there is then copied "
            "to the MDR and on to the CIR.",
        ),
        Q(
            "Which bus carries data in both directions between the processor and main memory?",
            ("Data bus", "Address bus", "Control bus", "Instruction bus"),
            0,
            "The data bus is bidirectional: it carries instructions and data from memory to "
            "the processor and results back to memory. The address bus only carries "
            "addresses from the processor, and the control bus carries control signals "
            "such as memory read and memory write.",
        ),
        Q(
            "What is the role of the Control Unit?",
            (
                "It performs arithmetic and logical operations on data",
                "It decodes instructions and sends control signals to coordinate the other "
                "components",
                "It temporarily stores the results of calculations",
                "It holds the address of the memory location being accessed",
            ),
            1,
            "The Control Unit decodes each instruction and sends control signals that "
            "coordinate the movement of data through the processor. Arithmetic and logic "
            "are carried out by the ALU, and results are held in the accumulator.",
        ),
        Q(
            "Which register holds an instruction while it is being decoded and executed?",
            (
                "Memory Data Register (MDR)",
                "Program Counter (PC)",
                "Current Instruction Register (CIR)",
                "Memory Address Register (MAR)",
            ),
            2,
            "After being fetched into the MDR, the instruction is copied to the Current "
            "Instruction Register, where it is split into its opcode and operand and "
            "decoded by the Control Unit.",
        ),
        Q(
            "Which statement describes Von Neumann architecture?",
            (
                "Instructions and data are stored in separate memory units with separate buses",
                "Instructions are executed directly from secondary storage",
                "Each instruction is held permanently in the processor's registers",
                "Instructions and data are stored together in the same memory and share the "
                "same buses",
            ),
            3,
            "In Von Neumann architecture a single memory and a single set of buses are "
            "shared by instructions and data. Separate memories and buses for instructions "
            "and data describe Harvard architecture.",
        ),
        Q(
            "What is pipelining?",
            (
                "Sharing one program equally between all the cores of a processor",
                "Storing frequently used instructions in cache memory",
                "Fetching the next instruction while the current one is decoded and the "
                "previous one is executed",
                "Raising the clock speed so that each cycle completes sooner",
            ),
            2,
            "Pipelining overlaps the stages of the fetch-decode-execute cycle so that "
            "several instructions are in progress at once. A branch can force the pipeline "
            "to be flushed, because the instructions already fetched are no longer needed.",
        ),
        Q(
            "A dual-core processor is replaced with a quad-core processor of the same clock "
            "speed. Why might a program not run twice as fast?",
            (
                "The clock speed halves whenever the number of cores doubles",
                "Parts of the program must run in sequence and cannot be shared between cores",
                "Each extra core halves the amount of cache available",
                "Quad-core processors cannot use pipelining",
            ),
            1,
            "Extra cores only help with work that can be carried out in parallel. Tasks "
            "that depend on the results of earlier steps must run sequentially, and "
            "coordinating the cores adds its own overhead.",
        ),
        Q(
            "Why does increasing the amount of cache memory usually improve processor "
            "performance?",
            (
                "More frequently used instructions and data can be held in fast memory close "
                "to the processor, so fewer slower fetches from RAM are needed",
                "The address bus becomes wider",
                "Programs no longer need to be loaded into RAM",
                "The clock speed of the processor increases",
            ),
            0,
            "Cache is small, very fast memory on or near the processor. The more it can "
            "hold, the more often the item needed is already in cache (a cache hit) rather "
            "than having to be fetched from slower main memory.",
        ),
        Q(
            "A processor has a 16-bit address bus. What is the maximum number of memory "
            "locations it can address directly?",
            ("16", "32,768", "65,536", "1,048,576"),
            2,
            "Each line of the address bus carries one bit, so 16 lines give 2^16 = 65,536 "
            "different addresses. Adding one more line doubles the number of locations "
            "that can be addressed.",
        ),
    ),
    # --- 1.1.2 Types of processor ----------------------------------------------------------
    "1.1.2": (
        Q(
            "Which statement describes a RISC processor when compared with a CISC processor?",
            (
                "It has a small set of simple instructions, each typically completed in one "
                "clock cycle",
                "It has many specialised instructions that each take several clock cycles",
                "It needs fewer lines of assembly code to carry out a task",
                "It cannot make use of pipelining",
            ),
            0,
            "RISC processors use a small set of simple, fixed-length instructions that each "
            "take about one clock cycle, which makes pipelining straightforward. CISC "
            "processors have larger sets of more complex instructions, so programs need "
            "fewer instructions but each takes longer.",
        ),
        Q(
            "Why are GPUs well suited to tasks such as machine learning and password cracking?",
            (
                "They have a higher clock speed than any CPU",
                "They contain a single very powerful core",
                "They can perform the same operation on many pieces of data in parallel",
                "They do not need to use RAM",
            ),
            2,
            "A GPU contains a large number of simple cores designed to apply the same "
            "instruction to many data items at once (SIMD). Tasks that repeat one "
            "calculation over a large data set can therefore be completed far faster than "
            "on a CPU.",
        ),
        Q(
            "What is a multicore processor?",
            (
                "A processor that uses more than one level of cache",
                "A processor that can run more than one operating system",
                "A processor whose clock speed changes while it is running",
                "A single chip containing several independent processing units, each able to "
                "fetch and execute its own instructions",
            ),
            3,
            "A multicore processor has two or more cores on one chip. Each core runs its "
            "own fetch-decode-execute cycle, so separate tasks, or separate parts of a "
            "suitably written program, can be processed at the same time.",
        ),
    ),
    # --- 1.1.3 Input, output and storage ---------------------------------------------------
    "1.1.3": (
        Q(
            "Why is a solid state drive more suitable than a magnetic hard disk for a laptop "
            "that is carried around?",
            (
                "It has a lower cost per gigabyte",
                "It has no moving parts, so it is more robust and uses less power",
                "It can be written to an unlimited number of times",
                "It stores data as pits and lands read by a laser",
            ),
            1,
            "Flash storage has no moving parts, so it is not damaged by knocks, runs "
            "silently, uses less power and gives faster access. Magnetic disks are cheaper "
            "per gigabyte, and flash cells wear out after a limited number of writes.",
        ),
        Q(
            "Which statement about RAM and ROM is correct?",
            (
                "RAM is non-volatile and ROM is volatile",
                "ROM holds the programs and data currently in use",
                "Both lose their contents when the power is turned off",
                "RAM is volatile and can be written to; ROM is non-volatile and typically "
                "holds the boot program",
            ),
            3,
            "RAM is volatile read-write memory holding the programs and data in use. ROM "
            "keeps its contents without power and usually stores the bootstrap program "
            "that starts the computer.",
        ),
        Q(
            "What is virtual storage?",
            (
                "Using part of secondary storage as an extension of RAM",
                "Memory built into the processor itself",
                "Storage accessed remotely over a network, such as cloud storage",
                "A backup copy held on optical media",
            ),
            2,
            "Virtual storage is storage held remotely and reached over a network or the "
            "internet, so it can be used from any connected device. Using secondary "
            "storage as an extension of RAM is virtual memory, which is a different idea.",
        ),
    ),
    # --- 1.2.1 Systems Software ------------------------------------------------------------
    "1.2.1": (
        Q(
            "How does paging differ from segmentation?",
            (
                "Paging divides memory into fixed-size blocks; segmentation divides it into "
                "variable-size logical sections",
                "Paging is used only for ROM; segmentation is used only for RAM",
                "Paging divides memory into logical sections; segmentation divides it into "
                "fixed-size blocks",
                "Paging stores data on disk; segmentation stores data in cache",
            ),
            0,
            "Pages are physical divisions of a fixed size, whereas segments are logical "
            "divisions that vary in size to match parts of a program. Both allow programs "
            "to be stored non-contiguously and to use virtual memory.",
        ),
        Q(
            "In round robin scheduling, what happens to a process that has not finished when "
            "its time slice ends?",
            (
                "It is terminated",
                "It keeps the processor until it completes",
                "It is moved to the back of the ready queue",
                "It is given a higher priority",
            ),
            2,
            "Each process receives a fixed time slice in turn. A process that is not "
            "complete when its slice ends is suspended and rejoins the back of the queue "
            "to wait for its next turn.",
        ),
        Q(
            "When an interrupt with a higher priority than the current task is detected, "
            "what happens to the contents of the processor's registers?",
            (
                "They are discarded",
                "They are copied to the hard disk",
                "They are sent to the device that raised the interrupt",
                "They are pushed onto a stack so that the task can be resumed later",
            ),
            3,
            "The register contents are pushed onto a stack and the address of the "
            "interrupt service routine is loaded into the Program Counter. When the "
            "routine finishes, the values are popped from the stack and the original task "
            "carries on.",
        ),
    ),
    # --- 1.2.2 Applications Generation -----------------------------------------------------
    "1.2.2": (
        Q(
            "How does a compiler differ from an interpreter?",
            (
                "A compiler translates and runs the code one line at a time",
                "A compiler translates the whole program into machine code before it is run",
                "A compiler can only translate assembly language",
                "A compiler must be present every time the program is run",
            ),
            1,
            "A compiler translates all of the source code in one go and produces an "
            "executable file that runs without the compiler. An interpreter translates and "
            "executes one line at a time and is needed every time the program runs.",
        ),
        Q(
            "What happens during the lexical analysis stage of compilation?",
            (
                "Machine code is produced",
                "Tokens are checked against the grammar rules of the language",
                "Comments and whitespace are removed and the code is converted into tokens",
                "The code is changed so that it runs faster or uses less memory",
            ),
            2,
            "Lexical analysis removes comments and whitespace, replaces keywords and "
            "identifiers with tokens and builds the symbol table. Checking the tokens "
            "against the rules of the language is syntax analysis, the next stage.",
        ),
        Q(
            "What is the purpose of a linker?",
            (
                "It combines compiled code with any library code it uses into a single "
                "executable",
                "It loads an executable file into main memory",
                "It translates assembly language into machine code",
                "It checks source code for syntax errors",
            ),
            0,
            "A linker joins the object code produced by the compiler with the code of any "
            "libraries it calls. Copying the finished executable into memory is the job of "
            "the loader, and translating assembly language is done by an assembler.",
        ),
    ),
    # --- 1.2.3 Software Development --------------------------------------------------------
    "1.2.3": (
        Q(
            "Which statement describes the waterfall lifecycle?",
            (
                "The software is developed in repeated cycles, each including risk analysis",
                "Working versions are released to the user every few weeks",
                "Programmers work in pairs with a user representative in the team",
                "Each stage is completed and signed off in sequence before the next begins",
            ),
            3,
            "In the waterfall model, analysis, design, implementation, testing and "
            "maintenance follow one another in a fixed order. It is simple to manage but "
            "makes it hard to respond to requirements that change part-way through.",
        ),
        Q(
            "Which methodology is most suitable for a large project with a high level of risk?",
            ("Waterfall", "Spiral", "Extreme programming", "Rapid application development"),
            1,
            "The spiral model includes a risk analysis in every cycle, so problems are "
            "found and dealt with early. This makes it suited to large, expensive, "
            "high-risk projects, although it needs staff skilled in risk assessment.",
        ),
        Q(
            "Which practice is a feature of extreme programming?",
            (
                "Producing all of the documentation before any coding begins",
                "Completing the analysis in full before any design work starts",
                "Pair programming with frequent small releases",
                "A formal risk analysis at the start of each cycle",
            ),
            2,
            "Extreme programming is an agile methodology. Programmers work in pairs, a "
            "user representative is part of the team, and working code is released "
            "frequently in small increments so that feedback can be acted on quickly.",
        ),
    ),
    # --- 1.2.4 Types of Programming Language -----------------------------------------------
    "1.2.4": (
        Q(
            "The Little Man Computer program shown is run. The user inputs 7 and then 3. "
            "What is output?",
            ("3", "4", "7", "10"),
            3,
            "The first input, 7, is stored in num. The second input, 3, is then in the "
            "accumulator. ADD num adds 7 to it, giving 10, which OUT displays.",
            code=_LMC_ADD_PROGRAM,
        ),
        Q(
            "In immediate addressing, what does the operand represent?",
            (
                "The address of the data to be used",
                "The actual value to be used",
                "The address of a location that holds the address of the data",
                "An offset to be added to the contents of the index register",
            ),
            1,
            "With immediate addressing the operand is the data itself. In direct "
            "addressing it is the address of the data, in indirect addressing it is the "
            "address of a location holding the address of the data, and in indexed "
            "addressing it is added to the index register.",
        ),
        Q(
            "In object-oriented programming, what is polymorphism?",
            (
                "Hiding attributes so that they can only be changed through methods",
                "A class taking on the attributes and methods of a parent class",
                "Methods with the same name behaving differently depending on the object "
                "they are called on",
                "Creating an object from a class",
            ),
            2,
            "Polymorphism means a method call can act in different ways according to the "
            "class of the object, for example when a subclass overrides a method. Hiding "
            "attributes is encapsulation, and taking on a parent's features is inheritance.",
        ),
    ),
    # --- 1.3.1 Compression, Encryption and Hashing -----------------------------------------
    "1.3.1": (
        Q(
            "Which of these is the run length encoding of the text AAAABBBCCD?",
            ("4A3B2C1D", "ABCD4321", "A4B3C2", "10ABCD"),
            0,
            "Run length encoding stores each run of repeated characters as a count "
            "followed by the character: four As, three Bs, two Cs and one D. It is a "
            "lossless method that works best on data with long runs.",
        ),
        Q(
            "Alice wants to send Bob a message that only Bob can read, using asymmetric "
            "encryption. Which key should she encrypt it with?",
            ("Alice's private key", "Alice's public key", "Bob's private key", "Bob's public key"),
            3,
            "A message encrypted with Bob's public key can only be decrypted with Bob's "
            "private key, which only Bob holds. Encrypting with Alice's private key would "
            "prove that she sent it, but anyone with her public key could read it.",
        ),
        Q(
            "Why are passwords stored as hashes rather than in encrypted form?",
            (
                "Hashes take up more storage, which makes them harder to steal",
                "A hash can be reversed only by the system administrator",
                "A hash function is one-way, so the original password cannot be recovered "
                "from the stored value",
                "Hashing compresses the password so that it is quicker to type",
            ),
            2,
            "Encryption is designed to be reversed with a key, so a stolen key exposes "
            "every password. A hash cannot be reversed: at login the password entered is "
            "hashed and the result compared with the stored hash.",
        ),
    ),
    # --- 1.3.2 Databases -------------------------------------------------------------------
    "1.3.2": (
        Q(
            "What is a primary key?",
            (
                "A field that uniquely identifies each record in a table",
                "A field used to link two tables together",
                "Any field that has been indexed",
                "The first field in a table",
            ),
            0,
            "A primary key is a field, or combination of fields, whose value is unique "
            "for every record, so each record can be identified without ambiguity.",
        ),
        Q(
            "What is a foreign key?",
            (
                "A field containing data imported from another database",
                "A field whose values are not unique",
                "A field in one table that is the primary key of another table",
                "A key made from two or more fields",
            ),
            2,
            "A foreign key is the primary key of one table appearing as a field in "
            "another. It creates the relationship between the two tables. A key made from "
            "several fields is a composite key.",
        ),
        Q(
            "Which condition must a table meet to be in first normal form?",
            (
                "It has no transitive dependencies",
                "It has no partial dependencies",
                "Every field depends on a foreign key",
                "It has no repeating groups and every field holds a single, atomic value",
            ),
            3,
            "First normal form requires atomic values, no repeating groups of fields and "
            "a primary key. Removing partial dependencies gives second normal form, and "
            "removing transitive dependencies gives third normal form.",
        ),
        Q(
            "A table is in second normal form. What else is needed for it to be in third "
            "normal form?",
            (
                "Every table has a composite primary key",
                "No non-key field depends on another non-key field",
                "All of the data is stored in a single table",
                "Every field is indexed",
            ),
            1,
            "Third normal form removes transitive dependencies: every non-key field must "
            "depend on the key, the whole key and nothing but the key.",
        ),
        Q(
            "Which SQL statement returns the surnames of all students in form 13A, in "
            "alphabetical order?",
            (
                "SELECT Student FROM Surname WHERE Form = '13A' SORT BY Surname",
                "SELECT Surname FROM Student ORDER BY Form = '13A'",
                "SELECT Surname FROM Student WHERE Form = '13A' ORDER BY Surname ASC",
                "SELECT * FROM Student WHERE Surname = '13A' ORDER BY Form",
            ),
            2,
            "SELECT names the field to return, FROM names the table, WHERE filters the "
            "records and ORDER BY ... ASC sorts them in ascending order. SORT BY is not an "
            "SQL keyword.",
        ),
        Q(
            "In the ACID properties of a transaction, what does atomicity guarantee?",
            (
                "Concurrent transactions do not interfere with one another",
                "Once committed, changes survive a system failure",
                "The database always moves from one valid state to another",
                "A transaction is either completed in full or not carried out at all",
            ),
            3,
            "Atomicity means a transaction cannot be left half done: if any part fails, "
            "all of it is rolled back. The other options describe isolation, durability "
            "and consistency.",
        ),
        Q(
            "What is the purpose of record locking?",
            (
                "To encrypt a record so that it cannot be read",
                "To prevent a record being edited by another user while it is already being "
                "changed",
                "To stop records from ever being deleted",
                "To speed up searches for a record",
            ),
            1,
            "Record locking stops two users changing the same record at the same time, "
            "which could cause one update to be lost. If two transactions each wait for a "
            "record the other has locked, deadlock can occur.",
        ),
        Q(
            "What does referential integrity ensure?",
            (
                "Every foreign key value matches a primary key value that exists in the "
                "linked table",
                "No two tables contain a field with the same name",
                "Every table is in third normal form",
                "Every field contains data of the correct type",
            ),
            0,
            "Referential integrity keeps related tables consistent. A record cannot refer "
            "to a record that does not exist, so, for example, a customer cannot be "
            "deleted while orders still refer to them.",
        ),
        Q(
            "Why is a secondary key used?",
            (
                "To uniquely identify each record",
                "To link two tables together",
                "To allow a field that is often searched to be indexed for faster searching",
                "To enforce referential integrity",
            ),
            2,
            "A secondary key is a field, not necessarily unique, that is indexed because "
            "it is frequently searched or sorted on, such as a surname. The index avoids "
            "having to check every record in turn.",
        ),
        Q(
            "A student can take many courses and each course has many students. How should "
            "this be represented in a relational database?",
            (
                "Store a list of course IDs in one field of the Student table",
                "Add a link table between Student and Course, giving two one-to-many "
                "relationships",
                "Merge Student and Course into a single table",
                "Make StudentID the primary key of the Course table",
            ),
            1,
            "A many-to-many relationship cannot be implemented directly. A link table "
            "holding the two foreign keys replaces it with two one-to-many relationships "
            "and keeps the database normalised.",
        ),
    ),
    # --- 1.3.3 Networks --------------------------------------------------------------------
    "1.3.3": (
        Q(
            "Which layer of the TCP/IP stack adds the source and destination IP addresses to "
            "each packet?",
            ("Application layer", "Transport layer", "Internet layer", "Link layer"),
            2,
            "The internet layer adds the source and destination IP addresses, and routers "
            "use the destination address to forward the packet. The link layer adds the "
            "MAC addresses of the devices at each end of the current hop.",
        ),
        Q(
            "What is the role of the transport layer in the TCP/IP stack?",
            (
                "It splits the data into packets, numbers them and checks that they all arrive",
                "It converts domain names into IP addresses",
                "It adds the MAC addresses of the sender and the recipient",
                "It selects the protocol, such as HTTP or FTP, that the data requires",
            ),
            0,
            "The transport layer uses TCP to split data into packets, add sequence "
            "numbers and port numbers, and request retransmission of any packets that are "
            "lost or corrupted.",
        ),
        Q(
            "What does the Domain Name System (DNS) do?",
            (
                "It assigns MAC addresses to devices",
                "It encrypts data sent between a browser and a web server",
                "It checks packets for errors",
                "It translates domain names into IP addresses",
            ),
            3,
            "People use domain names, but packets are routed using IP addresses. A DNS "
            "server looks up the domain name and returns the matching IP address, passing "
            "the request to another DNS server if it does not hold the record.",
        ),
        Q(
            "Which is a feature of packet switching?",
            (
                "A dedicated path is reserved for the whole of the communication",
                "Packets may take different routes and are reassembled at the destination",
                "Packets always arrive in the order in which they were sent",
                "Data can only travel in one direction",
            ),
            1,
            "In packet switching each packet is routed independently, so packets can take "
            "different routes and arrive out of order before being reassembled. Reserving "
            "a dedicated path describes circuit switching.",
        ),
        Q(
            "Which device forwards packets between different networks using IP addresses?",
            ("Switch", "Network interface card", "Router", "Wireless access point"),
            2,
            "A router connects networks and uses the destination IP address to decide "
            "where to send each packet next. A switch connects devices within one network "
            "and works with MAC addresses.",
        ),
        Q(
            "How does a switch decide where to send data on a local area network?",
            (
                "It sends everything to every device on the network",
                "It uses the destination IP address to choose a route across the internet",
                "It asks a DNS server for the location of the device",
                "It uses the destination MAC address to send the data only to the intended "
                "device",
            ),
            3,
            "A switch records the MAC address of the device on each of its ports and "
            "forwards data only to the port of the intended recipient, which reduces "
            "unnecessary traffic and collisions.",
        ),
        Q(
            "What does a firewall do?",
            (
                "It examines incoming and outgoing packets and blocks those that break its "
                "rules",
                "It scrambles data so that it cannot be understood if intercepted",
                "It removes viruses from files already saved on a computer",
                "It hides a device's MAC address from other devices",
            ),
            0,
            "A firewall sits between a network and the outside world and filters packets "
            "against a set of rules, for example by port or IP address, to prevent "
            "unauthorised access. Scrambling data is encryption.",
        ),
        Q(
            "Which is an advantage of a client-server network over a peer-to-peer network?",
            (
                "It needs no specialist hardware or staff",
                "The network is unaffected if the server fails",
                "Backups and security can be managed centrally",
                "Every device has equal status",
            ),
            2,
            "A central server makes it possible to manage files, backups, user accounts "
            "and security in one place. The drawbacks are the cost of the server and "
            "staff, and that the network depends on the server working.",
        ),
        Q(
            "Which statement describes a wide area network (WAN)?",
            (
                "It covers a single site and uses hardware owned by the organisation",
                "It can only use wireless connections",
                "It can connect a maximum of two networks",
                "It covers a large geographical area and usually relies on third-party "
                "communication links",
            ),
            3,
            "A WAN connects devices or networks over a large geographical area, usually "
            "using infrastructure leased from telecommunications companies. A LAN covers "
            "a small area with hardware owned by the organisation itself.",
        ),
        Q(
            "Why are network protocols arranged in layers?",
            (
                "So that data travels faster",
                "So that each layer can be developed or changed without affecting the others",
                "So that fewer IP addresses are needed",
                "So that packets do not need headers",
            ),
            1,
            "Layering divides a complex problem into self-contained parts. Each layer has "
            "one job and a defined interface, so a layer can be replaced or updated "
            "without changing the others, and equipment from different manufacturers can "
            "work together.",
        ),
    ),
    # --- 1.3.4 Web Technologies ------------------------------------------------------------
    "1.3.4": (
        Q(
            "Which CSS rule makes the text red in every element that has the class 'warning'?",
            (
                ".warning { color: red; }",
                "#warning { color: red; }",
                "warning { color: red; }",
                "<warning> { color: red; }",
            ),
            0,
            "A full stop selects by class, so .warning applies to every element with "
            'class="warning". A hash selects the single element with that id, and a bare '
            "name selects elements of that tag type.",
        ),
        Q(
            "According to the PageRank algorithm, which page is ranked most highly?",
            (
                "The page containing the most words",
                "The page that was updated most recently",
                "The page with the most outgoing links",
                "The page with many inbound links from pages that are themselves highly ranked",
            ),
            3,
            "PageRank treats a link to a page as a vote for it. Votes from pages with a "
            "high rank count for more, and the value of each vote is shared between all "
            "of the links leaving the page that casts it.",
        ),
        Q(
            "A web form validates its input using JavaScript in the browser. Why should the "
            "server validate the input as well?",
            (
                "JavaScript cannot check the length of an input",
                "Client-side code can be changed or bypassed by the user",
                "Server-side validation gives the user faster feedback",
                "Browsers cannot run code until the form has been sent",
            ),
            1,
            "Client-side validation gives quick feedback and reduces the load on the "
            "server, but a user can disable or alter it. Validation on the server is "
            "therefore still needed to protect against invalid or malicious data.",
        ),
    ),
    # --- 1.4.1 Data Types ------------------------------------------------------------------
    "1.4.1": (
        Q(
            "What is the denary value of the unsigned binary number 10110110?",
            ("91", "172", "182", "198"),
            2,
            "The place values of the 1 bits are 128, 32, 16, 4 and 2. "
            "128 + 32 + 16 + 4 + 2 = 182.",
        ),
        Q(
            "What is the 8-bit two's complement representation of denary -5?",
            ("10000101", "11111011", "11111010", "00000101"),
            1,
            "+5 is 00000101. Inverting the bits gives 11111010, and adding 1 gives "
            "11111011. As a check: -128 + 64 + 32 + 16 + 8 + 2 + 1 = -5.",
        ),
        Q(
            "What is the binary number 11010110 in hexadecimal?",
            ("D6", "C6", "DA", "6D"),
            0,
            "Split the byte into two nibbles: 1101 is 13, which is D, and 0110 is 6. The "
            "hexadecimal value is therefore D6.",
        ),
        Q(
            "An 8-bit number stored in sign and magnitude form is 10000111. What is its "
            "denary value?",
            ("135", "-121", "7", "-7"),
            3,
            "In sign and magnitude the leftmost bit is the sign (1 means negative) and "
            "the other seven bits are the size. 0000111 is 7, so the value is -7. Read as "
            "two's complement the same pattern would be -121.",
        ),
        Q(
            "What is the result of the binary addition 01101100 + 00110101?",
            ("10100001", "10011001", "10100011", "01100001"),
            0,
            "01101100 is 108 and 00110101 is 53. 108 + 53 = 161, which is "
            "128 + 32 + 1 = 10100001.",
        ),
        Q(
            "A floating point number is stored as a 4-bit two's complement mantissa followed "
            "by a 4-bit two's complement exponent. What is the denary value of 0110 0010?",
            ("0.75", "1.5", "3", "6"),
            2,
            "The mantissa 0.110 is 0.75 and the exponent 0010 is 2. Moving the binary "
            "point two places to the right gives 011.0, which is 3.",
        ),
        Q(
            "Which of these mantissas belongs to a normalised floating point number?",
            ("0011", "0101", "1101", "1110"),
            1,
            "A normalised mantissa begins with 01 if it is positive or 10 if it is "
            "negative, so the first two bits are always different. Only 0101 follows this "
            "rule. Normalising gives the greatest precision for the bits available.",
        ),
        Q(
            "What is the effect of a logical shift left of two places on an unsigned binary "
            "integer, assuming no bits are lost?",
            (
                "It divides the number by 2",
                "It multiplies the number by 2",
                "It divides the number by 4",
                "It multiplies the number by 4",
            ),
            3,
            "Each shift of one place to the left doubles the value, so two places "
            "multiply it by 4. Shifting to the right divides by 2 for each place.",
        ),
        Q(
            "Which mask and operation set the four most significant bits of a byte to 0 and "
            "leave the other four bits unchanged?",
            (
                "AND with 00001111",
                "OR with 00001111",
                "XOR with 11110000",
                "OR with 11110000",
            ),
            0,
            "ANDing a bit with 0 always gives 0, and ANDing it with 1 leaves it "
            "unchanged. OR with 1 sets a bit to 1, and XOR with 1 inverts it.",
        ),
        Q(
            "Why is Unicode often used in preference to ASCII?",
            (
                "It uses fewer bits for each character",
                "It can represent a far larger range of characters, covering many languages "
                "and symbols",
                "It is processed faster by the computer",
                "It only needs to store capital letters",
            ),
            1,
            "ASCII uses 7 bits, giving 128 characters, which is only enough for English "
            "letters, digits and some symbols. Unicode uses more bits per character and "
            "so can represent the characters of most of the world's languages, at the "
            "cost of more storage.",
        ),
    ),
    # --- 1.4.2 Data Structures -------------------------------------------------------------
    "1.4.2": (
        Q(
            "The items A, B and C are pushed onto an empty stack in that order. Which item is "
            "returned by the first pop?",
            ("A", "B", "C", "Nothing, because the stack is empty"),
            2,
            "A stack is a last in, first out structure. C was the last item pushed, so it "
            "is at the top of the stack and is the first to be popped.",
        ),
        Q(
            "The values 50, 30, 70 and 40 are inserted, in that order, into an empty binary "
            "search tree. Where is 40 placed?",
            (
                "As the left child of 30",
                "As the right child of 30",
                "As the left child of 70",
                "As the right child of 50",
            ),
            1,
            "50 is the root. 40 is less than 50, so move left to 30. 40 is greater than "
            "30 and 30 has no right child, so 40 becomes the right child of 30.",
        ),
        Q(
            "What is a collision in a hash table?",
            (
                "The table has no free locations left",
                "A key is searched for but is not in the table",
                "The same key is inserted twice",
                "Two different keys hash to the same location",
            ),
            3,
            "A hashing algorithm can map two different keys to the same location. The "
            "collision must be resolved, for example by storing the item in the next free "
            "location or by keeping a linked list at each location.",
        ),
    ),
    # --- 1.4.3 Boolean Algebra -------------------------------------------------------------
    "1.4.3": (
        Q(
            "Which expression is equivalent to NOT (A AND B)?",
            (
                "(NOT A) AND (NOT B)",
                "(NOT A) OR (NOT B)",
                "A OR B",
                "(NOT A) AND B",
            ),
            1,
            "This is one of De Morgan's laws: NOT (A AND B) is equivalent to "
            "(NOT A) OR (NOT B). To apply it, negate each term and swap AND for OR.",
        ),
        Q(
            "What does the expression A AND (A OR B) simplify to?",
            ("B", "A OR B", "A", "A AND B"),
            2,
            "This is the absorption law. If A is true the whole expression is true, and "
            "if A is false it is false, so the value of B makes no difference and the "
            "expression simplifies to A.",
        ),
        Q(
            "Which pair of expressions gives the sum (S) and carry (C) outputs of a half "
            "adder with inputs A and B?",
            (
                "S = A AND B, C = A XOR B",
                "S = A OR B, C = A AND B",
                "S = A XOR B, C = A OR B",
                "S = A XOR B, C = A AND B",
            ),
            3,
            "The sum is 1 when exactly one input is 1, which is XOR. The carry is 1 only "
            "when both inputs are 1, which is AND. A full adder also takes a carry in.",
        ),
    ),
    # --- 1.5.1 Computing-related legislation -----------------------------------------------
    "1.5.1": (
        Q(
            "Which Act makes it an offence to gain unauthorised access to a computer system?",
            (
                "The Data Protection Act 2018",
                "The Computer Misuse Act 1990",
                "The Copyright, Designs and Patents Act 1988",
                "The Regulation of Investigatory Powers Act 2000",
            ),
            1,
            "The Computer Misuse Act covers unauthorised access to computer material, "
            "unauthorised access with intent to commit a further offence, and "
            "unauthorised modification of material, such as spreading malware.",
        ),
        Q(
            "Which of these is a requirement of the Data Protection Act?",
            (
                "Personal data must be kept for at least ten years",
                "Personal data must be published on request",
                "Personal data must be accurate and kept no longer than necessary",
                "Personal data may be used for any purpose once it has been collected",
            ),
            2,
            "The Act requires personal data to be processed lawfully, collected for "
            "specified purposes, adequate and not excessive, accurate and up to date, "
            "kept no longer than necessary and kept secure.",
        ),
        Q(
            "What does the Regulation of Investigatory Powers Act allow?",
            (
                "Certain public bodies to monitor communications and to require internet "
                "service providers to assist them",
                "Anyone to copy software that they have bought",
                "Companies to sell customer data without consent",
                "Individuals to see the data an organisation holds about them",
            ),
            0,
            "RIPA sets out the powers of certain public bodies to carry out surveillance, "
            "including intercepting communications and requiring access to encrypted "
            "data. The right of individuals to see their data comes from the Data "
            "Protection Act.",
        ),
    ),
    # --- 1.5.2 Moral and ethical issues ----------------------------------------------------
    "1.5.2": (
        Q(
            "A bank uses an algorithm to decide automatically who is offered a loan. Which "
            "of these is an ethical concern?",
            (
                "The algorithm will be slower than a human",
                "The decisions may reflect bias in the data the algorithm was built on and "
                "can be hard to challenge",
                "Automated decisions always break the Computer Misuse Act",
                "The algorithm cannot process numbers",
            ),
            1,
            "An algorithm trained on biased historical data can repeat that bias, and it "
            "may be unclear who is accountable for a decision or how to appeal against "
            "it. The benefits are speed and consistency.",
        ),
        Q(
            "Which of these is an environmental impact of computing?",
            (
                "Computers have removed the need to generate electricity",
                "Data centres use almost no energy",
                "Devices never need to be replaced",
                "Discarded devices contain toxic materials that pollute if they are not "
                "recycled properly",
            ),
            3,
            "Electronic waste contains substances such as lead and mercury that are "
            "harmful if sent to landfill. Manufacturing devices and running data centres "
            "also use large amounts of energy and raw materials.",
        ),
        Q(
            "Why must a designer think about colour when building a website for an "
            "international audience?",
            (
                "Colours load more slowly in some countries",
                "Some character sets cannot display colour",
                "Colours can carry different meanings in different cultures",
                "Colour is illegal on commercial websites in some countries",
            ),
            2,
            "A colour seen as positive in one culture may be associated with danger or "
            "mourning in another. Layout, colour and character sets all need to suit the "
            "audience, including users who are colour-blind.",
        ),
    ),
}
